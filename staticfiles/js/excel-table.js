/**
 * Excel-like Table Visual Enhancements
 * Simplified version - only adds row numbers and keyboard navigation
 * Cell editing is handled by existing manageFormFields.js
 */

(function() {
  'use strict';

  // Initialize when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    initExcelTable();
  });

  function initExcelTable() {
    const table = document.getElementById('main-table');
    if (!table) return;

    // Enable column resizing
    enableColumnResizing();

    // Enable column actions (sort, filter, hide)
    enableColumnActions();

    // Enable column visibility management
    enableColumnVisibilityManagement();

    // Enable row actions (delete)
    enableRowActions();

    // Fix dropdown z-index in sticky column
    fixDropdownInStickyColumn();
  }

  /**
   * Update row numbers
   */
  function updateRowNumbers() {
    const tbody = document.querySelector('#main-table tbody');
    if (!tbody) return;

    const rows = tbody.querySelectorAll('tr');
    rows.forEach((row, index) => {
      const rowNumberSpan = row.querySelector('td:first-child .row-number');
      if (rowNumberSpan) {
        rowNumberSpan.textContent = index + 1;
      }
    });
  }

  /**
   * Enable column resizing
   */
  function enableColumnResizing() {
    const headers = document.querySelectorAll('#main-table thead th.resize-handle');
    
    headers.forEach(header => {
      let startX, startWidth;

      header.addEventListener('mousedown', function(e) {
        // Only resize when clicking on the right edge
        const rect = header.getBoundingClientRect();
        if (e.clientX < rect.right - 10) return;

        startX = e.clientX;
        startWidth = header.offsetWidth;

        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', stopResize);

        e.preventDefault();
      });

      function resize(e) {
        const width = startWidth + (e.clientX - startX);
        if (width > 50) { // Minimum width
          header.style.width = width + 'px';
          header.style.minWidth = width + 'px';
        }
      }

      function stopResize() {
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResize);
      }
    });
  }

  /**
   * Enable column actions (sort, filter, hide)
   */
  function enableColumnActions() {
    const table = document.getElementById('main-table');
    if (!table) return;

    // Sort ascending
    table.addEventListener('click', function(e) {
      if (e.target.closest('.sort-asc')) {
        e.preventDefault();
        const fieldName = e.target.closest('.sort-asc').getAttribute('data-field');
        sortColumn(fieldName, 'asc');
      }
    });

    // Sort descending
    table.addEventListener('click', function(e) {
      if (e.target.closest('.sort-desc')) {
        e.preventDefault();
        const fieldName = e.target.closest('.sort-desc').getAttribute('data-field');
        sortColumn(fieldName, 'desc');
      }
    });

    // Hide column
    table.addEventListener('click', function(e) {
      if (e.target.closest('.hide-column')) {
        e.preventDefault();
        const fieldName = e.target.closest('.hide-column').getAttribute('data-field');
        hideColumn(fieldName);
      }
    });

    // Filter column (placeholder)
    table.addEventListener('click', function(e) {
      if (e.target.closest('.filter-column')) {
        e.preventDefault();
        const fieldName = e.target.closest('.filter-column').getAttribute('data-field');
        alert('Функция фильтрации для поля "' + fieldName + '" будет добавлена позже');
      }
    });

    // Clear filter (placeholder)
    table.addEventListener('click', function(e) {
      if (e.target.closest('.clear-filter')) {
        e.preventDefault();
        alert('Фильтры очищены');
      }
    });
  }

  /**
   * Sort column
   */
  function sortColumn(fieldName, direction) {
    const tbody = document.querySelector('#main-table tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Get column index
    const headerCells = document.querySelectorAll('#main-table thead th');
    let columnIndex = -1;
    
    headerCells.forEach((th, index) => {
      const label = th.querySelector('.header-label');
      if (label) {
        const dropdown = th.querySelector('[data-field="' + fieldName + '"]');
        if (dropdown) {
          columnIndex = index;
        }
      }
    });

    if (columnIndex === -1) return;

    // Sort rows
    rows.sort((a, b) => {
      const cellA = a.children[columnIndex];
      const cellB = b.children[columnIndex];
      
      let valueA = cellA.textContent.trim();
      let valueB = cellB.textContent.trim();

      // Try to parse as numbers
      const numA = parseFloat(valueA.replace(/[^\d.-]/g, ''));
      const numB = parseFloat(valueB.replace(/[^\d.-]/g, ''));

      if (!isNaN(numA) && !isNaN(numB)) {
        return direction === 'asc' ? numA - numB : numB - numA;
      }

      // Compare as strings
      if (direction === 'asc') {
        return valueA.localeCompare(valueB, 'ru');
      } else {
        return valueB.localeCompare(valueA, 'ru');
      }
    });

    // Re-append rows
    rows.forEach(row => tbody.appendChild(row));

    // Re-number rows
    updateRowNumbers();

    // Show visual feedback
    showSortIndicator(columnIndex, direction);
  }

  /**
   * Show sort indicator
   */
  function showSortIndicator(columnIndex, direction) {
    // Remove all sort indicators
    document.querySelectorAll('.sort-indicator').forEach(el => el.remove());

    // Add new indicator
    const headerCells = document.querySelectorAll('#main-table thead th');
    const targetHeader = headerCells[columnIndex];
    
    if (targetHeader) {
      const indicator = document.createElement('span');
      indicator.className = 'sort-indicator';
      indicator.innerHTML = direction === 'asc' ? ' ▲' : ' ▼';
      indicator.style.fontSize = '10px';
      indicator.style.marginLeft = '4px';
      
      const label = targetHeader.querySelector('.header-label');
      if (label) {
        label.appendChild(indicator);
      }
    }
  }

  /**
   * Hide column
   */
  function hideColumn(fieldName) {
    const headerCells = document.querySelectorAll('#main-table thead th');
    let columnIndex = -1;
    
    headerCells.forEach((th, index) => {
      const dropdown = th.querySelector('[data-field="' + fieldName + '"]');
      if (dropdown) {
        columnIndex = index;
      }
    });

    if (columnIndex === -1) return;

    // Hide header
    headerCells[columnIndex].style.display = 'none';

    // Hide all cells in this column
    const rows = document.querySelectorAll('#main-table tbody tr, #main-table tfoot tr');
    rows.forEach(row => {
      if (row.children[columnIndex]) {
        row.children[columnIndex].style.display = 'none';
      }
    });

    // Update checkbox in visibility menu
    const checkbox = document.querySelector('.column-visibility-toggle[data-field="' + fieldName + '"]');
    if (checkbox) {
      checkbox.checked = false;
    }
  }

  /**
   * Show column
   */
  function showColumn(fieldName) {
    const headerCells = document.querySelectorAll('#main-table thead th');
    let columnIndex = -1;
    
    headerCells.forEach((th, index) => {
      const dropdown = th.querySelector('[data-field="' + fieldName + '"]');
      if (dropdown) {
        columnIndex = index;
      }
    });

    if (columnIndex === -1) return;

    // Show header
    headerCells[columnIndex].style.display = '';

    // Show all cells in this column
    const rows = document.querySelectorAll('#main-table tbody tr, #main-table tfoot tr');
    rows.forEach(row => {
      if (row.children[columnIndex]) {
        row.children[columnIndex].style.display = '';
      }
    });
  }

  /**
   * Enable column visibility management
   */
  function enableColumnVisibilityManagement() {
    // Toggle column visibility with checkboxes
    document.addEventListener('change', function(e) {
      if (e.target.classList.contains('column-visibility-toggle')) {
        const fieldName = e.target.getAttribute('data-field');
        if (e.target.checked) {
          showColumn(fieldName);
        } else {
          hideColumn(fieldName);
        }
      }
    });

    // Show all columns button
    const showAllBtn = document.getElementById('showAllColumns');
    if (showAllBtn) {
      showAllBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Check all checkboxes
        const checkboxes = document.querySelectorAll('.column-visibility-toggle');
        checkboxes.forEach(checkbox => {
          if (!checkbox.checked) {
            checkbox.checked = true;
            showColumn(checkbox.getAttribute('data-field'));
          }
        });
      });
    }
  }

  /**
   * Enable row actions (delete, edit)
   */
  function enableRowActions() {
    const table = document.getElementById('main-table');
    if (!table) return;

    // Delete order
    table.addEventListener('click', function(e) {
      if (e.target.closest('.delete-order')) {
        e.preventDefault();
        const deleteBtn = e.target.closest('.delete-order');
        const orderId = deleteBtn.getAttribute('data-id');
        
        if (confirm('Вы уверены, что хотите удалить этот заказ?')) {
          deleteOrder(orderId);
        }
      }
    });
  }

  /**
   * Delete order via AJAX
   */
  function deleteOrder(orderId) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/orders/order/${orderId}/delete/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
    })
    .then(response => {
      if (response.ok) {
        // Remove row from table
        const row = document.querySelector(`#main-table tbody tr[data-id="${orderId}"]`);
        if (row) {
          row.remove();
          // Re-number remaining rows
          updateRowNumbers();
        }
        // Show success message
        alert('Заказ успешно удален');
      } else {
        alert('Ошибка при удалении заказа');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Ошибка при удалении заказа');
    });
  }

  /**
   * Fix dropdown positioning in sticky column
   */
  function fixDropdownInStickyColumn() {
    const table = document.getElementById('main-table');
    if (!table) return;

    // Handle dropdown positioning using MutationObserver
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        mutation.addedNodes.forEach(function(node) {
          if (node.nodeType === 1 && node.classList && node.classList.contains('dropdown-menu-actions')) {
            if (node.classList.contains('show')) {
              positionDropdown(node);
            }
          }
        });
        
        if (mutation.target.classList && mutation.target.classList.contains('dropdown-menu-actions')) {
          if (mutation.target.classList.contains('show')) {
            positionDropdown(mutation.target);
          }
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class']
    });

    // Also listen to click events on dropdown triggers
    table.addEventListener('click', function(e) {
      const trigger = e.target.closest('[data-bs-toggle="dropdown"]');
      if (trigger) {
        setTimeout(function() {
          const dropdown = trigger.nextElementSibling;
          if (dropdown && dropdown.classList.contains('dropdown-menu-actions') && dropdown.classList.contains('show')) {
            positionDropdown(dropdown);
          }
        }, 10);
      }
    });
  }

  /**
   * Position dropdown menu using fixed positioning
   */
  function positionDropdown(dropdownMenu) {
    // Find the trigger button
    const trigger = dropdownMenu.previousElementSibling;
    if (!trigger) return;

    const rect = trigger.getBoundingClientRect();
    const dropdownHeight = dropdownMenu.offsetHeight;
    const viewportHeight = window.innerHeight;
    
    // Calculate position
    let top = rect.bottom + 2;
    
    // If dropdown would go below viewport, show it above the trigger
    if (top + dropdownHeight > viewportHeight) {
      top = rect.top - dropdownHeight - 2;
    }
    
    dropdownMenu.style.position = 'fixed';
    dropdownMenu.style.top = top + 'px';
    dropdownMenu.style.left = rect.left + 'px';
    dropdownMenu.style.zIndex = '99999';
    
    console.log('Dropdown positioned:', { top: top, left: rect.left });
  }

  // Make functions available globally if needed
  window.ExcelTable = {
    updateRowNumbers,
    sortColumn,
    hideColumn,
    showColumn
  };

})();
