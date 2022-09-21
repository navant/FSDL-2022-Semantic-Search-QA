from semantic_search_qa.utils import chunk_text, pdf2text


def test_pdf2text():
    expected_output = "hola\nque\ntal\nestas?"
    text = pdf2text("./tests/sample.pdf")
    assert text == expected_output


def test_chunk_text():
    text = pdf2text("./tests/sample.pdf")
    chunked_text = chunk_text(text, 4)
    assert chunked_text[0] == "hola"
    assert chunked_text[1] == "\nque"
    assert chunked_text[2] == "\ntal"
    assert chunked_text[3] == "\nest"
    assert chunked_text[4] == "as?"

    # Test overlapping
    chunked_text = chunk_text(text, 4, do_overlap=True, overlap_size=1)
    assert chunked_text[0] == "hola"
    assert chunked_text[1] == "a\nqu"
    assert chunked_text[2] == "ue\nt"
    assert chunked_text[3] == "tal\n"
    assert chunked_text[4] == "\nest"
    assert chunked_text[5] == "tas?"
