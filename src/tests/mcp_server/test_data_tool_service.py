"""
Tests for DataToolService path traversal protection and file operations.
"""

import os
import tempfile
from services.data_tool_service import DataToolService


def test_data_tool_service_normal_and_traversal():
    with tempfile.TemporaryDirectory() as tmp_dir, tempfile.TemporaryDirectory() as outside_dir:
        # Create a valid allowed CSV file in dataset directory
        valid_file_path = os.path.join(tmp_dir, "product_table.csv")
        with open(valid_file_path, "w", encoding="utf-8") as f:
            f.write("id,name\n1,Widget\n")

        # Create a secret file in the outside directory
        secret_file_path = os.path.join(outside_dir, "secret.txt")
        with open(secret_file_path, "w", encoding="utf-8") as f:
            f.write("top secret data")

        # Create a symlink inside dataset directory pointing outside to secret file
        symlink_path = os.path.join(tmp_dir, "customer_profile.csv")
        try:
            os.symlink(secret_file_path, symlink_path)
            symlink_created = True
        except (OSError, AttributeError):
            symlink_created = False

        service = DataToolService(dataset_path=tmp_dir)

        # 1. Normal valid file find
        found_path = service._find_file("product_table.csv")
        assert found_path is not None
        assert os.path.realpath(found_path) == os.path.realpath(valid_file_path)

        # 2. Symlink path traversal attempt (if symlink creation succeeded)
        if symlink_created:
            traversal_path = service._find_file("customer_profile.csv")
            assert traversal_path is None, "Path traversal via symlink should be blocked"

        # 3. File not in dataset
        missing_path = service._find_file("non_existent.csv")
        assert missing_path is None
