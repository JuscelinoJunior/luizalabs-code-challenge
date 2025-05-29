import pytest
import json
from unittest.mock import patch, mock_open, Mock
from fastapi import HTTPException
from app.services import get_mock_product, fetch_product_data
import httpx
from app.utils import verify_password


def test_get_mock_product_success():
    mock_data = json.dumps([
        {"id": "123", "title": "Test"}
    ])
    with patch("builtins.open", mock_open(read_data=mock_data)):
        product = get_mock_product("123", mock_path="any/path.json")
        assert product["title"] == "Test"

def test_get_mock_product_not_found():
    mock_data = json.dumps([
        {"id": "999", "title": "Other Test"}
    ])
    with patch("builtins.open", mock_open(read_data=mock_data)):
        product = get_mock_product("123", mock_path="any/path.json")
        assert product is None

def test_get_mock_product_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(HTTPException) as exc:
            get_mock_product("123", mock_path="invalid.json")
        assert exc.value.status_code == 500
        assert "not found" in str(exc.value.detail)

def test_get_mock_product_invalid_json():
    with patch("builtins.open", mock_open(read_data="{invalid json")):
        with pytest.raises(HTTPException) as exc:
            get_mock_product("123")
        assert exc.value.status_code == 500
        assert "Invalid JSON" in str(exc.value.detail)

@patch("app.services.get_mock_product")
def test_fetch_product_data_test_mode(mock_get_mock_product):
    mock_get_mock_product.return_value = {"id": "123", "title": "Teste"}
    product = fetch_product_data("123", test_products=True)
    assert product["title"] == "Teste"
    mock_get_mock_product.assert_called_once_with("123")


@patch("httpx.get")
def test_fetch_product_data_real_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": "456", "title": "API Product"}
    mock_get.return_value.raise_for_status.return_value = None

    result = fetch_product_data("456", test_products=False)
    assert result["title"] == "API Product"


@patch("httpx.get")
def test_fetch_product_data_real_failure(mock_get):
    mock_response = Mock()
    mock_response.status_code = 503
    mock_response.reason_phrase = "Service Unavailable"

    mock_request = Mock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Service Unavailable",
        request=mock_request,
        response=mock_response,
    )

    mock_get.return_value = mock_response

    with pytest.raises(HTTPException) as exc_info:
        fetch_product_data("456", test_products=False)

    assert exc_info.value.status_code == 503
    assert "Product API service unavailable" in str(exc_info.value.detail)

@patch("app.utils.pwd_context.verify")
def test_verify_password_success(mock_verify):
    mock_verify.return_value = True
    result = verify_password("plain123", "hashed123")
    assert result is True
    mock_verify.assert_called_once_with("plain123", "hashed123")

@patch("app.utils.pwd_context.verify")
def test_verify_password_failure(mock_verify):
    mock_verify.return_value = False
    result = verify_password("wrongpassword", "hashed123")
    assert result is False
    mock_verify.assert_called_once_with("wrongpassword", "hashed123")