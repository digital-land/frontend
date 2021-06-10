from digital_land_frontend.jinja_filters.mappers import Mapper


class ContributionPurposeMapper(Mapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/developer-contributions-collection/dataset/contribution-purpose.csv"
    ]
    key_field = "contribution-purpose"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class ContributionFundingStatusMapper(Mapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/developer-contributions-collection/dataset/contribution-funding-status.csv"
    ]
    key_field = "contribution-funding-status"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class PlanTypeMapper(Mapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/development-plan-type-collection/dataset/development-plan-type.csv"
    ]
    key_field = "development-plan-type"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class PolicyCategoryMapper(Mapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/development-policy-category-collection/dataset/development-policy-category.csv"
    ]
    key_field = "development-policy-category"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class DeveloperAgreementTypeMapper(Mapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/developer-contributions-collection/dataset/developer-agreement-type.csv"
    ]
    key_field = "developer-agreement-type"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class DocumentTypeMapper(Mapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/document-type-collection/dataset/document-type.csv"
    ]
    key_field = "category"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))
