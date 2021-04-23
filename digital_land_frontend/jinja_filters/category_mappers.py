from digital_land_frontend.jinja_filters.mappers import Mapper


class ContributionPurposeMapper(Mapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/developer-contributions-collection/main/dataset/contribution-purpose.csv"
    ]
    key_field = "contribution-purpose"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class ContributionFundingStatusMapper(Mapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/contribution-funding-status/main/dataset/contribution-funding-status.csv"
    ]
    key_field = "contribution-funding-status"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class PlanTypeMapper(Mapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/development-plan-type-collection/main/dataset/development-plan-type.csv"
    ]
    key_field = "development-plan-type"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class PolicyCategoryMapper(Mapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/development-policy-category-collection/main/dataset/development-policy-category.csv"
    ]
    key_field = "development-policy-category"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class DeveloperAgreementTypeMapper(Mapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/developer-agreement-type/main/dataset/developer-agreement-type.csv"
    ]
    key_field = "developer-agreement-type"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class DocumentTypeMapper(Mapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/document-type/main/dataset/document-type.csv"
    ]
    key_field = "category"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))
