from marqo.errors import MarqoWebError
from tests.marqo_test import MarqoTestCase, CloudTestIndex


class TestModelCacheManagement(MarqoTestCase):
    MODEL = "ViT-B/32"

    # NOTE: The cuda should already have model loaded in the startup
    def test_get_cuda_info(self) -> None:
        try:
            settings = {"model": self.MODEL}
            test_index_name = self.create_test_index(
                cloud_test_index_to_use=CloudTestIndex.image_index,
                open_source_test_index_name=self.generic_test_index_name,
                open_source_index_kwargs=settings
            )
            res = self.client.index(test_index_name).get_cuda_info()
            if "cuda_devices" not in res:
                raise AssertionError
        # catch error if no cuda device in marqo
        except MarqoWebError:
            pass

    def test_get_cpu_info(self) -> None:
        settings = {"model": self.MODEL}
        test_index_name = self.create_test_index(
            cloud_test_index_to_use=CloudTestIndex.image_index,
            open_source_test_index_name=self.generic_test_index_name,
            open_source_index_kwargs=settings
        )
        res = self.client.index(test_index_name).get_cpu_info()

        if "cpu_usage_percent" not in res:
            raise AssertionError

        if "memory_used_percent" not in res:
            raise AssertionError

        if "memory_used_gb" not in res:
            raise AssertionError

    def test_get_loaded_models(self) -> None:
        settings = {"model": self.MODEL}
        test_index_name = self.create_test_index(
            cloud_test_index_to_use=CloudTestIndex.image_index,
            open_source_test_index_name=self.generic_test_index_name,
            open_source_index_kwargs=settings
        )
        res = self.client.index(test_index_name).get_loaded_models()

        if "models" not in res:
            raise AssertionError

    def test_eject_no_cached_model(self) -> None:
        # test a model that is not cached
        try:
            settings = {"model": self.MODEL}
            test_index_name = self.create_test_index(
                cloud_test_index_to_use=CloudTestIndex.image_index,
                open_source_test_index_name=self.generic_test_index_name,
                open_source_index_kwargs=settings
            )
            res = self.client.index(test_index_name).eject_model("void_model", "void_device")
            raise AssertionError
        except MarqoWebError:
            pass

    def test_eject_model(self) -> None:
        if self.IS_MULTI_INSTANCE:
            self.skipTest("Test will sometimes fail on marqo multi instance setup")

        settings = {"model": self.MODEL}

        test_index_name = self.create_test_index(
            cloud_test_index_to_use=CloudTestIndex.image_index,
            open_source_test_index_name=self.generic_test_index_name,
            open_source_index_kwargs=settings
        )
        d1 = {
            "doc title": "Cool Document 1",
            "field 1": "some extra info"
        }
        self.client.index(test_index_name).add_documents([d1], device="cpu", tensor_fields=["doc title", "field 1"])
        res = self.client.index(test_index_name).eject_model(self.MODEL, "cpu")
        assert res["result"] == "success"
        assert res["message"].startswith("successfully eject")



