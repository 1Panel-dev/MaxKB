class SnapshotQuery:
    """Evaluate the queryset predicates against mixed-source regression fixtures."""

    def __init__(self, documents):
        self.documents = documents

    def filter(self, **filters):
        def matches(document):
            for lookup, expected in filters.items():
                value = document
                parts = lookup.split("__")
                less_than = parts[-1] == "lt"
                for field in parts[:-1] if less_than else parts:
                    value = value.get(field) if isinstance(value, dict) else getattr(value, field, None)
                if less_than:
                    if not value < expected:
                        return False
                elif value != expected:
                    return False
            return True

        return SnapshotQuery([document for document in self.documents if matches(document)])

    def none(self):
        return SnapshotQuery([])

    def values_list(self, field, flat=False):
        return [getattr(document, field) for document in self.documents]

    def count(self):
        return len(self.documents)

    def __iter__(self):
        return iter(self.documents)
