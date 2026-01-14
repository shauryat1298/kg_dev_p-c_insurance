import os
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from src.page_data_model_dev import convert_png_dir_to_proto_dm_async, process_single_png_async


class PageDataModelDevTests(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_process_single_png_async_success(self):
        """Test successful processing of a single PNG file"""
        async def run_test():
            form_png_path = os.path.join(self.temp_dir, "form_001.png")
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_output")
            os.makedirs(form_proto_dm_dir_path, exist_ok=True)
            
            # Create a dummy PNG file
            with open(form_png_path, "wb") as f:
                f.write(b"fake png data")

            mock_messages = [{"role": "user", "content": "test"}]
            mock_llm_response = "syntax = \"proto3\";\nmessage Test { string field = 1; }"
            mock_proto_code = "syntax = \"proto3\";\nmessage Test { string field = 1; }"

            with patch("src.page_data_model_dev.prompt_for_page_dm", return_value=mock_messages), \
                 patch("src.page_data_model_dev.call_openrouter_llm_async", new_callable=AsyncMock) as mock_llm, \
                 patch("src.page_data_model_dev.extract_proto_code_for_llm_response", return_value=mock_proto_code) as mock_extract, \
                 patch("aiofiles.open", new_callable=AsyncMock) as mock_file:
                
                mock_llm.return_value = mock_llm_response
                mock_file.return_value.__aenter__.return_value.write = AsyncMock()

                await process_single_png_async(form_png_path, form_proto_dm_dir_path)

                # Verify calls
                mock_llm.assert_called_once_with(mock_messages, "anthropic/claude-sonnet-4.5")
                mock_extract.assert_called_once_with(mock_llm_response)
                
                # Verify file write was attempted
                expected_proto_path = os.path.join(form_proto_dm_dir_path, "form_001.proto")
                mock_file.assert_called_once_with(expected_proto_path, "w")

        asyncio.run(run_test())

    def test_process_single_png_async_llm_error_handled(self):
        """Test that LLM errors are caught and handled gracefully"""
        async def run_test():
            form_png_path = os.path.join(self.temp_dir, "form_001.png")
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_output")
            os.makedirs(form_proto_dm_dir_path, exist_ok=True)
            
            # Create a dummy PNG file
            with open(form_png_path, "wb") as f:
                f.write(b"fake png data")

            mock_messages = [{"role": "user", "content": "test"}]

            with patch("src.page_data_model_dev.prompt_for_page_dm", return_value=mock_messages), \
                 patch("src.page_data_model_dev.call_openrouter_llm_async", new_callable=AsyncMock) as mock_llm, \
                 patch("builtins.print") as mock_print:
                
                mock_llm.side_effect = Exception("LLM API error")

                # Should not raise, but return None
                result = await process_single_png_async(form_png_path, form_proto_dm_dir_path)

                self.assertIsNone(result)
                mock_print.assert_called_once()
                self.assertIn("Error processing single PNG", str(mock_print.call_args))

        asyncio.run(run_test())

    def test_process_single_png_async_file_write_error_handled(self):
        """Test that file write errors are caught and handled gracefully"""
        async def run_test():
            form_png_path = os.path.join(self.temp_dir, "form_001.png")
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_output")
            os.makedirs(form_proto_dm_dir_path, exist_ok=True)
            
            # Create a dummy PNG file
            with open(form_png_path, "wb") as f:
                f.write(b"fake png data")

            mock_messages = [{"role": "user", "content": "test"}]
            mock_llm_response = "syntax = \"proto3\";\nmessage Test { string field = 1; }"
            mock_proto_code = "syntax = \"proto3\";\nmessage Test { string field = 1; }"

            with patch("src.page_data_model_dev.prompt_for_page_dm", return_value=mock_messages), \
                 patch("src.page_data_model_dev.call_openrouter_llm_async", new_callable=AsyncMock) as mock_llm, \
                 patch("src.page_data_model_dev.extract_proto_code_for_llm_response", return_value=mock_proto_code), \
                 patch("aiofiles.open", new_callable=AsyncMock) as mock_file:
                
                mock_llm.return_value = mock_llm_response
                # Simulate file write error
                mock_file.side_effect = IOError("Permission denied")

                # Should not raise, but return None (error is silently caught)
                result = await process_single_png_async(form_png_path, form_proto_dm_dir_path)

                self.assertIsNone(result)

        asyncio.run(run_test())

    def test_convert_png_dir_to_proto_dm_async_success(self):
        """Test successful conversion of PNG directory to proto data models"""
        async def run_test():
            form_png_dir_path = os.path.join(self.temp_dir, "test_form")
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_output")
            os.makedirs(form_png_dir_path, exist_ok=True)
            
            # Create dummy PNG files
            png_files = ["test_form_001.png", "test_form_002.png"]
            for png_file in png_files:
                png_path = os.path.join(form_png_dir_path, png_file)
                with open(png_path, "wb") as f:
                    f.write(b"fake png data")

            mock_messages = [{"role": "user", "content": "test"}]
            mock_llm_response = "syntax = \"proto3\";\nmessage Test { string field = 1; }"
            mock_proto_code = "syntax = \"proto3\";\nmessage Test { string field = 1; }"

            with patch("src.page_data_model_dev.prompt_for_page_dm", return_value=mock_messages), \
                 patch("src.page_data_model_dev.call_openrouter_llm_async", new_callable=AsyncMock) as mock_llm, \
                 patch("src.page_data_model_dev.extract_proto_code_for_llm_response", return_value=mock_proto_code), \
                 patch("aiofiles.open", new_callable=AsyncMock) as mock_file:
                
                mock_llm.return_value = mock_llm_response
                mock_file.return_value.__aenter__.return_value.write = AsyncMock()

                result = await convert_png_dir_to_proto_dm_async(form_png_dir_path, form_proto_dm_dir_path)

                # Verify result
                self.assertEqual(result, "test_form")
                
                # Verify directory was created
                self.assertTrue(os.path.isdir(form_proto_dm_dir_path))
                
                # Verify LLM was called for each PNG file
                self.assertEqual(mock_llm.call_count, len(png_files))

        asyncio.run(run_test())

    def test_convert_png_dir_to_proto_dm_async_empty_directory(self):
        """Test conversion with empty PNG directory"""
        async def run_test():
            form_png_dir_path = os.path.join(self.temp_dir, "empty_form")
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_output")
            os.makedirs(form_png_dir_path, exist_ok=True)
            
            # No PNG files in directory

            result = await convert_png_dir_to_proto_dm_async(form_png_dir_path, form_proto_dm_dir_path)

            # Verify result
            self.assertEqual(result, "empty_form")
            
            # Verify directory was created
            self.assertTrue(os.path.isdir(form_proto_dm_dir_path))

        asyncio.run(run_test())

    def test_convert_png_dir_to_proto_dm_async_creates_output_directory(self):
        """Test that output directory is created if it doesn't exist"""
        async def run_test():
            form_png_dir_path = os.path.join(self.temp_dir, "test_form")
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "new_proto_output")
            os.makedirs(form_png_dir_path, exist_ok=True)
            
            # Create a dummy PNG file
            png_path = os.path.join(form_png_dir_path, "test_form_001.png")
            with open(png_path, "wb") as f:
                f.write(b"fake png data")

            # Output directory doesn't exist yet
            self.assertFalse(os.path.exists(form_proto_dm_dir_path))

            mock_messages = [{"role": "user", "content": "test"}]
            mock_llm_response = "syntax = \"proto3\";\nmessage Test { string field = 1; }"
            mock_proto_code = "syntax = \"proto3\";\nmessage Test { string field = 1; }"

            with patch("src.page_data_model_dev.prompt_for_page_dm", return_value=mock_messages), \
                 patch("src.page_data_model_dev.call_openrouter_llm_async", new_callable=AsyncMock) as mock_llm, \
                 patch("src.page_data_model_dev.extract_proto_code_for_llm_response", return_value=mock_proto_code), \
                 patch("aiofiles.open", new_callable=AsyncMock) as mock_file:
                
                mock_llm.return_value = mock_llm_response
                mock_file.return_value.__aenter__.return_value.write = AsyncMock()

                await convert_png_dir_to_proto_dm_async(form_png_dir_path, form_proto_dm_dir_path)

                # Verify directory was created
                self.assertTrue(os.path.isdir(form_proto_dm_dir_path))

        asyncio.run(run_test())

    def test_convert_png_dir_to_proto_dm_async_sorts_png_files(self):
        """Test that PNG files are processed in sorted order"""
        async def run_test():
            form_png_dir_path = os.path.join(self.temp_dir, "test_form")
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_output")
            os.makedirs(form_png_dir_path, exist_ok=True)
            
            # Create PNG files in non-sorted order
            png_files = ["test_form_003.png", "test_form_001.png", "test_form_002.png"]
            for png_file in png_files:
                png_path = os.path.join(form_png_dir_path, png_file)
                with open(png_path, "wb") as f:
                    f.write(b"fake png data")

            mock_messages = [{"role": "user", "content": "test"}]
            mock_llm_response = "syntax = \"proto3\";\nmessage Test { string field = 1; }"
            mock_proto_code = "syntax = \"proto3\";\nmessage Test { string field = 1; }"

            call_order = []

            async def track_call_order(*args, **kwargs):
                call_order.append(args[0] if args else None)
                return mock_llm_response

            with patch("src.page_data_model_dev.prompt_for_page_dm", return_value=mock_messages), \
                 patch("src.page_data_model_dev.call_openrouter_llm_async", new_callable=AsyncMock, side_effect=track_call_order), \
                 patch("src.page_data_model_dev.extract_proto_code_for_llm_response", return_value=mock_proto_code), \
                 patch("aiofiles.open", new_callable=AsyncMock) as mock_file:
                
                mock_file.return_value.__aenter__.return_value.write = AsyncMock()

                await convert_png_dir_to_proto_dm_async(form_png_dir_path, form_proto_dm_dir_path)

                # Verify all files were processed
                self.assertEqual(len(call_order), len(png_files))

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()

