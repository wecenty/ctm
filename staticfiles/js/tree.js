let treeViewInstance = null;

function initializeTree(currentItemId) {
    $.ajax({
        url: treeDataUrl,
        success: function (data) {
            const savedState = JSON.parse(localStorage.getItem('treeViewState') || '[]');

            // Инициализация дерева с обработчиками событий
            $('#tree').treeview({
                data: processTreeData(data),
                levels: 1,
                showIcon: false,
                expandIcon: 'bi bi-chevron-right',
                collapseIcon: 'bi bi-chevron-down',
                selectedBackColor: '#0d6efd',
                onhoverColor: '#e8f9fa',
                onNodeExpanded: function (event, data) {
                    // When a node is expanded
                    const state = JSON.parse(localStorage.getItem('treeViewState') || '[]');
                    if (!state.includes(data.nodeId)) {
                        state.push(data.nodeId);
                        localStorage.setItem('treeViewState', JSON.stringify(state));
                    }
                },
                onNodeCollapsed: function (event, data) {
                    // When a node is collapsed
                    const state = JSON.parse(localStorage.getItem('treeViewState') || '[]');
                    const index = state.indexOf(data.nodeId);
                    if (index > -1) {
                        state.splice(index, 1);
                        localStorage.setItem('treeViewState', JSON.stringify(state));
                    }
                }
            });

            // Get tree instance
            treeViewInstance = $('#tree').treeview(true);

            // Restore expanded state
            savedState.forEach(nodeId => {
                $('#tree').treeview('expandNode', [nodeId, {silent: true}]);
            });

            // Add click handlers
            $('#tree').on('nodeSelected', function (event, data) {
                if (data.href) {
                    const currentState = $('#tree').treeview('getExpanded').map(node => node.nodeId);
                    localStorage.setItem('treeViewState', JSON.stringify(currentState));
                    window.location.href = data.href;
                }
            });

            // If we have a current item, reveal its path
            if (currentItemId) {
                expandToNode(currentItemId);
            }
        }
    });

    initializeSearch();
}

function processTreeData(nodes) {
    return nodes.map(node => ({
        text: node.text,
        href: node.href,
        itemId: node.itemId,
        type: node.type,
        selectable: true,
        state: {
            expanded: false
        },
        nodes: node.nodes && node.nodes.length > 0 ? processTreeData(node.nodes) : undefined
    }));
}

function expandToNode(itemId) {
    const findNodeAndParents = function (nodes, targetId, parents = []) {
        for (let i = 0; i < nodes.length; i++) {
            const node = nodes[i];
            if (node.itemId === targetId) {
                return {node, parents};
            }
            if (node.nodes) {
                const result = findNodeAndParents(node.nodes, targetId, [...parents, node]);
                if (result) return result;
            }
        }
        return null;
    };

    const allNodes = $('#tree').treeview('getNodes');
    const result = findNodeAndParents(allNodes, itemId);

    if (result) {
        // Expand all parent nodes
        result.parents.forEach(parent => {
            $('#tree').treeview('expandNode', [parent.nodeId, {silent: true}]);

            // Update saved state
            const state = JSON.parse(localStorage.getItem('treeViewState') || '[]');
            if (!state.includes(parent.nodeId)) {
                state.push(parent.nodeId);
                localStorage.setItem('treeViewState', JSON.stringify(state));
            }
        });

        // Select the target node
        $('#tree').treeview('selectNode', [result.node.nodeId, {silent: true}]);

        // Scroll to the selected node
        setTimeout(() => {
            const element = $(`#tree [data-nodeid="${result.node.nodeId}"]`);
            if (element.length) {
                element[0].scrollIntoView({behavior: 'smooth', block: 'nearest'});
            }
        }, 100);
    }
}

function initializeSearch() {
    let searchTimeout = null;
    const searchInput = $('#projectSearch');
    const searchResults = $('#searchResults');
    const clearButton = $('#clearSearch');

    searchInput.on('input', function () {
        const query = $(this).val().trim();

        clearTimeout(searchTimeout);

        if (query.length < 2) {
            searchResults.addClass('d-none').empty();
            clearButton.hide();
            return;
        }

        clearButton.show();
        searchTimeout = setTimeout(() => {
            $.ajax({
                url: '/api/search/',
                data: {query: query},
                success: function (results) {
                    if (results.length > 0) {
                        const html = results.map(result => `
                            <div class="search-result-item" data-url="${result.url}">
                                <div>${result.name}</div>
                            </div>
                        `).join('');

                        searchResults.html(html).removeClass('d-none');

                        $('.search-result-item').on('click', function () {
                            // Save tree state before navigation
                            const currentState = $('#tree').treeview('getExpanded').map(node => node.nodeId);
                            localStorage.setItem('treeViewState', JSON.stringify(currentState));
                            window.location.href = $(this).data('url');
                        });
                    } else {
                        searchResults.html('<div class="no-results">Ничего не найдено</div>')
                            .removeClass('d-none');
                    }
                }
            });
        }, 300);
    });

    // Handle click outside search results
    $(document).on('click', function (e) {
        if (!$(e.target).closest('#searchResults, #projectSearch').length) {
            searchResults.addClass('d-none');
        }
    });

    // Clear search
    clearButton.on('click', function () {
        searchInput.val('');
        searchResults.addClass('d-none').empty();
        $(this).hide();
    });

    // Handle Escape key
    searchInput.on('keydown', function (e) {
        if (e.key === 'Escape') {
            searchInput.val('');
            searchResults.addClass('d-none').empty();
            clearButton.hide();
        }
    });
}