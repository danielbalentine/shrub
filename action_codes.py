class ActionCode:
    def __init__(self, code_str: str):
        self.raw = code_str
        self.requires_uid_check = code_str.endswith('*')
        self.chain = code_str.rstrip('*').split('/')
        self.conditional = len(self.chain) > 1

        self._dispatch = {
            'D': self._replace_dummy,
            'Z': self._replace_empty,
            'X': self._remove,
            'K': self._keep,
            'C': self._clean,
            'U': self._replace_uid,
        }

    def apply(self, dataset, tag):
        code = self.chain[0]
        return self._dispatch[code](dataset, tag)

    def _replace_dummy(self, dataset, tag):
        ...  # needs VR-aware dummy value

    def _replace_empty(self, dataset, tag):
        ...  # this one's genuinely simple, del/blank the value

    def _remove(self, dataset, tag):
        ...  # del dataset[tag], recurse if Sequence

    def _keep(self, dataset, tag):
        ...  # no-op, or recurse if Sequence (per the standard's own note on K)

    def _clean(self, dataset, tag):
        raise NotImplementedError('needs VR-aware clean-value mapping')

    def _replace_uid(self, dataset, tag):
        raise NotImplementedError('needs per-run UID consistency cache')