from typing import TYPE_CHECKING

from django.db import models

from api.models.Metadata import BaseMetadata

if TYPE_CHECKING:
    from api.models.Dataset import Dataset


class DatasetMetadata(BaseMetadata):
    dataset = models.ForeignKey(
        "api.Dataset",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="metadata",
    )

    def __str__(self) -> str:
        return f"{self.dataset.title} - {self.metadata_item.label}"

    class Meta(BaseMetadata.Meta):
        db_table = "dataset_metadata"
        unique_together = ("dataset", "metadata_item")
