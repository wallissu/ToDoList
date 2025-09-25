document.addEventListener('DOMContentLoaded', function() {
        const cards = document.querySelectorAll('.card');
        const columns = document.querySelectorAll('.column');
        let draggedCard = null;
        
        // DRAG START - Quando começa a arrastar
        cards.forEach(card => {
            card.addEventListener('dragstart', function(e) {
                draggedCard = this;
                this.classList.add('dragging');
                e.dataTransfer.setData('text/plain', this.dataset.cardId);
            });
            
            card.addEventListener('dragend', function() {
                this.classList.remove('dragging');
                columns.forEach(col => col.classList.remove('drop-zone'));
            });
        });
        
        // DRAG OVER - Quando está sobre uma coluna
        columns.forEach(column => {
            column.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('drop-zone');
            });
            
            column.addEventListener('dragleave', function() {
                this.classList.remove('drop-zone');
            });
            
            // DROP - Quando solta o card
            column.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drop-zone');
                
                if (draggedCard) {
                    const cardId = draggedCard.dataset.cardId;
                    const destinationColumn = this;
                    const destinationColumnName = destinationColumn.dataset.column;
                    const container = destinationColumn.querySelector('.cards-container');
                    
                    // CALCULAR POSIÇÃO baseada na coordenada Y
                    const visiblesCards = container.querySelectorAll('.card:not(.dragging)');
                    const containerRect = container.getBoundingClientRect();
                    const mouseY = e.clientY - containerRect.top;
                    
                    let newPosition = visiblesCards.length; // Posição padrão: final
                    
                    // Encontrar entre quais cards soltou
                    for (let i = 0; i < visiblesCards.length; i++) {
                        const cardRect = visiblesCards[i].getBoundingClientRect();
                        const cardMiddleY = cardRect.top - containerRect.top + (cardRect.height / 2);
                        
                        if (mouseY < cardMiddleY) {
                            newPosition = i;
                            break;
                        }
                    }
                    
                    // MOVER VISUALMENTE para a nova posição
                    if (newPosition >= visiblesCards.length) {
                        container.appendChild(draggedCard);
                    } else {
                        container.insertBefore(draggedCard, visiblesCards[newPosition]);
                    }
                    
                    // SALVAR NO BANCO
                    updateDBposition(cardId, destinationColumnName, newPosition);
                }
            });
        });
        
        // FUNÇÃO PARA SALVAR NO BANCO
        function updateDBposition(cardId, column, position) {
            fetch('/update_position/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    card_id: cardId,
                    column: column,
                    position: position
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status !== 'success') {
                    console.error('Erro:', data.message);
                    alert('Erro ao salvar posição. Recarregando...');
                    setTimeout(() => location.reload(), 1000);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro de conexão. Recarregando...');
                setTimeout(() => location.reload(), 1000);
            });
        }
        
        // PEGAR TOKEN CSRF
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    });