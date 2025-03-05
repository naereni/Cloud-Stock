function submitForm() {
    document.getElementById('product-form').submit();
}

// Обработчик клика на кнопку загрузки, чтобы вызвать выбор файла
document.getElementById('upload-button').addEventListener('click', function () {
    document.getElementById('file-upload').click();
});

// Обработчик выбора файла
document.getElementById('file-upload').addEventListener('change', function () {
    if (this.files.length > 0) {
        // Получаем выбранный файл
        const file = this.files[0];
        
        // Логирование имени файла (по желанию)
        console.log('Файл выбран: ', file.name);

        // Создаем объект FileReader для чтения содержимого файла
        const reader = new FileReader();
        
        // Обработчик завершения чтения файла
        reader.onload = function (e) {
            // Обновляем изображение на странице
            const currentPhotoImg = document.getElementById('current-photo-img');
            currentPhotoImg.src = e.target.result;
        };
        
        // Читаем файл как Data URL
        reader.readAsDataURL(file);
    }
});