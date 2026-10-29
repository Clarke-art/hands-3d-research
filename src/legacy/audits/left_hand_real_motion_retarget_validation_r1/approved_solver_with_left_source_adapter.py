def arr(mat):
    return [list(row) for row in mat]

def norm(v):
    return Vector(v).normalized()

def frame(y, x):
    y = norm(y)
    x = Vector(x) - y * Vector(x).dot(y)
    x.normalize()
    z = x.cross(y).normalized()
    return Matrix((x, y, z)).transposed()

def signed(a, b, h):
    a = norm(a)
    b = norm(b)
    h = norm(h)
    return math.atan2(a.cross(b).dot(h), a.dot(b))

class Solver:

    def __init__(self, ob, rig, iteration=1):
        self.ob = ob
        self.rig = rig
        self.iteration = iteration
        src = ROOT / 'references/piano_motion/pianovam_sample_r1/Handskeleton/2024-03-04_03-46-36.json'
        acq = read(PREV / 'PIANOVAM_SINGLE_SAMPLE_ACQUISITION_R1_STATUS.json')
        expected = next((f['sha256'] for f in acq['files'] if f['remote_path'].startswith('Handskeleton/')))
        assert sha(src) == expected
        data = read(src)
        self.points = []
        self.palms = []
        self.local = []
        for f in range(690, 1111):
            p = np.array(data[str(f)]['Right'], dtype=float)
            p[:, 0] *= -1
            assert p.shape == (21, 3)
            p[:, 1] *= 1080 / 1920
            P = frame(Vector(p[9] - p[0]), Vector(p[5] - p[17]))
            self.points.append(p)
            self.palms.append(P)
            self.local.append(np.array([(P.transposed() @ Vector(v - p[0]))[:] for v in p]))
        self.local = np.array(self.local)
        self.rest = {b.name: b.matrix_local.to_3x3().normalized() for b in rig.data.bones}
        self.y = {n: R @ Vector((0, 1, 0)) for n, R in self.rest.items()}
        p = {b.name: b.head_local for b in rig.data.bones}
        self.R = frame(p['MIDDLE_MCP_R'] - p['WRIST_R'], p['INDEX_MCP_R'] - p['LITTLE_MCP_R'])
        self.bridge = self.R @ self.palms[0].transposed()
        self.rad = self.R @ Vector((1, 0, 0))
        self.normal = self.R @ Vector((0, 0, 1))
        self.distal = self.R @ Vector((0, 1, 0))
        self.anatom = {}
        self.hinges = {}
        self.calibration = {}
        self.digits = [('INDEX', 5), ('MIDDLE', 9), ('RING', 13), ('LITTLE', 17)]
        for digit, start in self.digits:
            n = digit + '_MCP_R'
            A = frame(self.y[n], self.rad)
            self.anatom[n] = A
            self.calibration[n] = A.transposed() @ self.rest[n]
            h = A @ Vector((1, 0, 0))
            for j in ['PIP', 'DIP']:
                n = digit + '_' + j + '_R'
                hh = (h - self.y[n] * h.dot(self.y[n])).normalized()
                self.hinges[n] = self.rest[n].transposed() @ hh
        anchor = np.median(self.local[:, 1, :2] - self.local[:, 0, :2], axis=0)
        self.thumb_neutral = norm((anchor[0], anchor[1], 0))
        if iteration == 2:
            dirs = self.local[:, 2] - self.local[:, 1]
            dirs /= np.linalg.norm(dirs, axis=1)[:, None]
            self.thumb_neutral = norm(np.median(dirs, axis=0))
        self.thumb_src_rest = frame(self.thumb_neutral, (0, 0, 1))
        self.thumb_anatom = frame(self.y['THUMB_CMC_R'], self.normal)
        self.thumb_roll_offset = self.thumb_anatom.transposed() @ self.rest['THUMB_CMC_R']
        h = self.thumb_anatom @ Vector((1, 0, 0))
        for j in ['MCP', 'IP']:
            n = 'THUMB_' + j + '_R'
            hh = (h - self.y[n] * h.dot(self.y[n])).normalized()
            self.hinges[n] = self.rest[n].transposed() @ hh
        self.source_sha = expected
        self.cache = {}

    def raw(self, i):
        if i in self.cache:
            return self.cache[i]
        L = self.local[i]
        D = self.bridge @ self.palms[i] @ self.palms[0].transposed() @ self.bridge.transposed()
        world = {}
        qs = {}
        components = {}
        world['WRIST_R'] = D @ self.rest['WRIST_R']
        qs['WRIST_R'] = (self.rest['WRIST_R'].transposed() @ world['WRIST_R']).to_quaternion()
        for digit, s in self.digits:
            d = norm(L[s + 1] - L[s])
            n = digit + '_MCP_R'
            S = frame(d, (1, 0, 0))
            A = self.anatom[n]
            target = D @ A @ S @ self.calibration[n]
            predicted = world['WRIST_R'] @ self.rest['WRIST_R'].transposed() @ self.rest[n]
            q = (predicted.transposed() @ target).to_quaternion()
            qs[n] = q
            world[n] = target
            flex = math.atan2(d.z, math.hypot(d.x, d.y))
            abd = math.atan2(d.x, d.y)
            components[n] = {'source_flexion_rad': flex, 'source_abduction_rad': abd, 'source_flexion_deg': math.degrees(flex), 'source_abduction_deg': math.degrees(abd), 'source_plane_anchor': 'palm radial projected perpendicular to first phalanx', 'rig_anatomical_rest_frame': arr(A), 'rig_local_flexion_axis': list(self.rest[n].transposed() @ (A @ Vector((1, 0, 0)))), 'rig_local_positive_abduction_axis': list(self.rest[n].transposed() @ -(A @ Vector((0, 0, 1))))}
            for j, joint in [(1, 'PIP'), (2, 'DIP')]:
                parent = n
                n = digit + '_' + joint + '_R'
                a = norm(L[s + j] - L[s + j - 1])
                b = norm(L[s + j + 1] - L[s + j])
                h = norm(Vector((1, 0, 0)) - a * a.x)
                bend = signed(a, b, h)
                q = Quaternion(self.hinges[n], bend)
                qs[n] = q
                pred = world[parent] @ self.rest[parent].transposed() @ self.rest[n]
                world[n] = pred @ q.to_matrix()
                components[n] = {'source_signed_hinge_bend_rad': bend, 'source_signed_hinge_bend_deg': math.degrees(bend), 'rig_local_hinge_axis': list(self.hinges[n]), 'source_out_of_digit_plane_component': float(b.dot(h))}
        a = norm(L[2] - L[1])
        b = norm(L[3] - L[2])
        plane = a.cross(b)
        plane_mag = plane.length
        anchor = norm(Vector((0, 0, 1)) - a * a.z)
        reliable = plane_mag > math.sin(math.radians(10)) and abs(norm(plane).dot(anchor)) > 0.7
        T = frame(a, (0, 0, 1))
        delta = self.thumb_src_rest.transposed() @ T
        target = D @ self.thumb_anatom @ delta @ self.thumb_roll_offset
        n = 'THUMB_CMC_R'
        predicted = world['WRIST_R'] @ self.rest['WRIST_R'].transposed() @ self.rest[n]
        qs[n] = (predicted.transposed() @ target).to_quaternion()
        world[n] = target
        swing = self.thumb_neutral.rotation_difference(a)
        components[n] = {'source_base_neutral_direction': list(self.thumb_neutral), 'source_CMC_direction': list(a), 'source_swing_quaternion': list(swing), 'source_in_palm_swing_rad': math.atan2(a.x, a.y) - math.atan2(self.thumb_neutral.x, self.thumb_neutral.y), 'source_out_of_palm_flexion_rad': math.atan2(a.z, math.hypot(a.x, a.y)), 'thumb_plane_normal': list(norm(plane)) if plane_mag > 1e-07 else None, 'thumb_plane_reliable_for_bend_diagnostic': reliable, 'CMC_axial_twist_copied': False}
        for u, joint in [(2, 'MCP'), (3, 'IP')]:
            parent = n
            n = 'THUMB_' + joint + '_R'
            a = norm(L[u] - L[u - 1])
            b = norm(L[u + 1] - L[u])
            h = norm(Vector((0, 0, 1)) - a * a.z)
            bend = signed(a, b, h)
            qs[n] = Quaternion(self.hinges[n], bend)
            pred = world[parent] @ self.rest[parent].transposed() @ self.rest[n]
            world[n] = pred @ qs[n].to_matrix()
            components[n] = {'source_signed_hinge_bend_rad': bend, 'source_signed_hinge_bend_deg': math.degrees(bend), 'rig_local_hinge_axis': list(self.hinges[n]), 'thumb_plane_anchor': 'palm normal projected perpendicular to parent segment', 'out_of_thumb_plane_component': float(b.dot(h))}
        for q in qs.values():
            q.normalize()
        self.cache[i] = (qs, components)
        return self.cache[i]

    def smoothed(self, i):
        seq = [self.raw(max(0, i - 1))[0], self.raw(i)[0], self.raw(min(420, i + 1))[0]]
        out = {}
        for n, q in seq[1].items():
            neighbors = [s[n].copy() for s in seq]
            for p in neighbors:
                if p.dot(q) < 0:
                    p.negate()
            v = [sum((w * p[k] for w, p in zip([0.25, 0.5, 0.25], neighbors))) for k in range(4)]
            s = Quaternion(v)
            s.normalize()
            out[n] = s
        return (out, self.raw(i)[1])
