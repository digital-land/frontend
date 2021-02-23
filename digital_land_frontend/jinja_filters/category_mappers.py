from digital_land_frontend.jinja_filters.mappers import Mapper


class ContributionPurposeMapper(Mapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/contribution-purpose/main/dataset/contribution-purpose.csv"
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
