import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.pdf_to_img import convert_pdf_to_png, process_single_pdf


class FakePixmap:
    def __init__(self, content: bytes = b"pixeldata"):
        self.content = content

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.content)


class FakePage:
    def __init__(self, pixmap: FakePixmap | None = None):
        self.pixmap = pixmap or FakePixmap()

    def get_pixmap(self, dpi: int = 600) -> FakePixmap:
        return self.pixmap


class FakePdf:
    def __init__(self, pages: list[FakePage | Exception]):
        self.pages = pages
        self.closed = False

    def __len__(self) -> int:
        return len(self.pages)

    def load_page(self, index: int) -> FakePage:
        page = self.pages[index]
        if isinstance(page, Exception):
            raise page
        return page

    def close(self) -> None:
        self.closed = True


class PdfToImgTests(unittest.TestCase):
    def test_convert_pdf_to_png_writes_all_pages(self) -> None:
        fake_pdf = FakePdf([FakePage(), FakePage()])

        with tempfile.TemporaryDirectory() as tmpdir, patch("src.pdf_to_img.fitz.open", return_value=fake_pdf):
            result = convert_pdf_to_png("dummy.pdf", tmpdir)

            expected_base = os.path.join(tmpdir, "dummy")
            first_image = f"{expected_base}_001.png"
            second_image = f"{expected_base}_002.png"

            self.assertEqual(result, "dummy")
            self.assertTrue(os.path.isfile(first_image))
            self.assertTrue(os.path.isfile(second_image))
            self.assertTrue(fake_pdf.closed)

    def test_convert_pdf_to_png_continues_after_page_error(self) -> None:
        fake_pdf = FakePdf([FakePage(), RuntimeError("page failure"), FakePage()])

        with tempfile.TemporaryDirectory() as tmpdir, patch("src.pdf_to_img.fitz.open", return_value=fake_pdf):
            result = convert_pdf_to_png("example.pdf", tmpdir)

            first_image = os.path.join(tmpdir, "example_001.png")
            third_image = os.path.join(tmpdir, "example_003.png")

            self.assertEqual(result, "example")
            self.assertTrue(os.path.isfile(first_image))
            self.assertTrue(os.path.isfile(third_image))
            # Ensure the failing page did not produce an output file
            self.assertFalse(os.path.isfile(os.path.join(tmpdir, "example_002.png")))

    def test_process_single_pdf_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "file.pdf")
            open(pdf_path, "wb").close()

            with patch("src.pdf_to_img.convert_pdf_to_png", autospec=True) as mock_convert:
                mock_convert.return_value = "file"

                name, ok, error = process_single_pdf(pdf_path, tmpdir)

                self.assertEqual(name, "file")
                self.assertTrue(ok)
                self.assertIsNone(error)
                expected_dir = os.path.join(tmpdir, "file")
                self.assertTrue(os.path.isdir(expected_dir))
                mock_convert.assert_called_once_with(pdf_path, expected_dir)

    def test_process_single_pdf_failure_propagates_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "bad.pdf")
            open(pdf_path, "wb").close()

            with patch("src.pdf_to_img.convert_pdf_to_png", side_effect=ValueError("boom")):
                name, ok, error = process_single_pdf(pdf_path, tmpdir)

                self.assertEqual(name, pdf_path)
                self.assertFalse(ok)
                self.assertIn("boom", error)


if __name__ == "__main__":
    unittest.main()

