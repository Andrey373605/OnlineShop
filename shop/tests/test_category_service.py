import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from shop.app.services.category_service import CategoryService
from shop.app.shemas.category_shemas import CategoryCreate, CategoryUpdate


class TestCategoryService:
    """Тесты для CategoryService"""

    @pytest.fixture
    def mock_conn(self):
        """Фикстура для мока соединения с БД"""
        return AsyncMock()

    @pytest.fixture
    def category_data(self):
        """Фикстура с тестовыми данными категории"""
        return {
            "id": 1,
            "name": "Test Category"
        }

    @pytest.mark.asyncio
    async def test_create_category_success(self, mock_conn, category_data):
        """Тест успешного создания категории"""
        # Arrange
        with patch('shop.app.services.category_service.queries.create_category') as mock_create:
            mock_create.return_value = category_data
            data = CategoryCreate(name="Test Category")

            # Act
            result = await CategoryService.create_category(mock_conn, data)

            # Assert
            mock_create.assert_called_once_with(mock_conn, name="Test Category")
            assert result == {"id": 1, "message": "Category created successfully"}

    @pytest.mark.asyncio
    async def test_create_category_failure(self, mock_conn):
        """Тест неудачного создания категории"""
        # Arrange
        with patch('shop.app.services.category_service.queries.create_category') as mock_create:
            mock_create.return_value = None
            data = CategoryCreate(name="Test Category")

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await CategoryService.create_category(mock_conn, data)

            assert exc_info.value.status_code == 500
            assert "Failed to create product" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_category_by_id_success(self, mock_conn, category_data):
        """Тест успешного получения категории по ID"""
        # Arrange
        with patch('shop.app.services.category_service.queries.get_category_by_id') as mock_get:
            mock_get.return_value = category_data

            # Act
            result = await CategoryService.get_category_by_id(mock_conn, 1)

            # Assert
            mock_get.assert_called_once_with(mock_conn, id=1)
            assert result == category_data

    @pytest.mark.asyncio
    async def test_get_category_by_id_not_found(self, mock_conn):
        """Тест получения несуществующей категории"""
        # Arrange
        with patch('shop.app.services.category_service.queries.get_category_by_id') as mock_get:
            mock_get.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await CategoryService.get_category_by_id(mock_conn, 999)

            assert exc_info.value.status_code == 404
            assert "Category not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_all_categories_success(self, mock_conn, category_data):
        """Тест успешного получения всех категорий"""
        # Arrange
        with patch('shop.app.services.category_service.queries.get_all_categories') as mock_get_all:
            categories = [category_data, {**category_data, "id": 2, "name": "Category 2"}]
            mock_get_all.return_value = categories

            # Act
            result = await CategoryService.get_all_categories(mock_conn)

            # Assert
            mock_get_all.assert_called_once_with(mock_conn)
            assert result == categories
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_categories_empty(self, mock_conn):
        """Тест получения пустого списка категорий"""
        # Arrange
        with patch('shop.app.services.category_service.queries.get_all_categories') as mock_get_all:
            mock_get_all.return_value = []

            # Act
            result = await CategoryService.get_all_categories(mock_conn)

            # Assert
            assert result == []
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_update_category_success(self, mock_conn, category_data):
        """Тест успешного обновления категории"""
        # Arrange
        with patch('shop.app.services.category_service.queries.update_category') as mock_update:
            mock_update.return_value = category_data
            data = CategoryUpdate(name="Updated Category")

            # Act
            result = await CategoryService.update_category(mock_conn, 1, data)

            # Assert
            mock_update.assert_called_once_with(mock_conn, id=1, name="Updated Category")
            assert result == {"id": 1, "message": "Category updated successfully"}

    @pytest.mark.asyncio
    async def test_update_category_not_found(self, mock_conn):
        """Тест обновления несуществующей категории"""
        # Arrange
        with patch('shop.app.services.category_service.queries.update_category') as mock_update:
            mock_update.return_value = None
            data = CategoryUpdate(name="Updated Category")

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await CategoryService.update_category(mock_conn, 999, data)

            assert exc_info.value.status_code == 404
            assert "Category not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_delete_category_success(self, mock_conn, category_data):
        """Тест успешного удаления категории"""
        # Arrange
        with patch('shop.app.services.category_service.queries.delete_category') as mock_delete:
            mock_delete.return_value = category_data

            result = await CategoryService.delete_category(mock_conn, 1)

            mock_delete.assert_called_once_with(mock_conn, id=1)
            assert result == {"id": 1, "message": "Category deleted successfully"}

    @pytest.mark.asyncio
    async def test_delete_category_not_found(self, mock_conn):
        """Тест удаления несуществующей категории"""
        # Arrange
        with patch('shop.app.services.category_service.queries.delete_category') as mock_delete:
            mock_delete.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await CategoryService.delete_category(mock_conn, 999)

            assert exc_info.value.status_code == 404
            assert "Category not found" in str(exc_info.value.detail)