import os


class TestAddress:
    ethereum = os.getenv("ETHEREUM_TEST_ADDRESS")

    @classmethod
    def get_ethereum(cls):
        if cls.ethereum is not None:
            return cls.ethereum
        else:
            raise ValueError(
                "ETHEREUM_TEST_ADDRESS is not set"
            )

