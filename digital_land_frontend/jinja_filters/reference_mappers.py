import logging

logger = logging.getLogger(__name__)


class ReferenceMapper:
    xref_datasets = {"geography", "category", "policy", "document"}

    def __init__(self, view_model, specification):
        self.view_model = view_model
        self.specification = specification

    def get_references_by_slug_id(self, slug_id, field):
        result = {}
        field_typology = self.specification.field_typology(field)

        logger.debug('looking for "%s" relationships', field_typology)
        for row in self.view_model.get_references_by_id(field_typology, str(slug_id)):
            result.setdefault(row["type"], []).append(
                {
                    "id": row["id"],
                    "reference": row["reference"],
                    "href": row["href"],
                    "text": row["name"],
                }
            )

        return result

    def get_references(self, value, field):
        """
        Returns links to each entity that references the provided id in the provided field

        E.g.
        "article-4-document", "document-type" -> [
            {"reference": "article-4-document:CA05-1", "href": "/conservation-area/local-authority-eng/LBH/CA05", "text": "article-4-document:CA05-1"},
            {"reference": "article-4-document:CA11-2", "href": "/conservation-area/local-authority-eng/LBH/CA11", "text": "article-4-document:CA11-2"},
            ...
        ]
        """
        field_typology = self.specification.field_typology(field)
        if field_typology not in self.xref_datasets:
            logger.info("no relationships configured for %s typology", field_typology)
            return {}

        key = list(self.view_model.get_id(field_typology, value))

        if key and "type" in key[0]:
            key = [id for id in key if id["type"] == field]

        row_count = len(key)
        if row_count != 1:
            logger.warning(
                'select %s "%s" returned %s rows, expected exactly 1',
                field_typology,
                value,
                row_count,
            )
            return {}
        key_id = key[0]["id"]

        return self.get_references_by_slug_id(key_id, field)
