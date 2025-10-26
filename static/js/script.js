// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s, transform 0.5s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(400px)';
            
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

// Preview de imagem antes de fazer upload
document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const currentImageDiv = input.parentElement.querySelector('.current-image');
                if (currentImageDiv) {
                    const img = currentImageDiv.querySelector('img');
                    if (img) {
                        img.src = e.target.result;
                    }
                } else {
                    const preview = document.createElement('div');
                    preview.className = 'current-image';
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview"><p>Nova imagem selecionada</p>`;
                    input.parentElement.insertBefore(preview, input);
                }
            };
            reader.readAsDataURL(file);
        }
    });
});
