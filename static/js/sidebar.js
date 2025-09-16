


(function() {
// 1) Initialize any menus on the page
    function initMenus() {
        KTMenu.createInstances('#kt_app_sidebar');
    }


    function findActiveLink(menuEl, normalizedPath) {
        for (let link of menuEl.querySelectorAll('a.menu-link[href]')) {
        let href = link.getAttribute('href');
        if (!href || href === '#') continue;
        try {
            let url = new URL(href, window.location.origin);
            let p = url.pathname;
            if (!p.endsWith('/')) p += '/';
            if (p === normalizedPath) {
            return link;
            }
        } catch (e) {
            // skip bad URLs
        }
        }
        return null;
    }
    // 2) Sync the active link + open only its dropdown chain
    function syncActiveMenu() {
        // Normalize current path
        let path = window.location.pathname;

        
        if (!path.endsWith('/')) path += '/';

        // Grab the very first menu instance on the page
        const menuEl = document.querySelector('#kt_app_sidebar');
        if (!menuEl) return;
        const menu = KTMenu.getInstance(menuEl);

        // 2a) Hide all open dropdowns/accordions
        KTMenu.hideDropdowns();
        // var menuElement = menu.getElement();
        // console.log('Menu element:', menuElement);
        // 2b) Find the <a.menu-link> that matches this path & set it active
        // const activeLink = menu.getLinkByAttribute(path, 'href');
        // console.log('Active link:', activeLink);
        const activeLink = findActiveLink(menuEl, path);

        if (activeLink) {
        menu.setActiveLink(activeLink);
            
        // 2c) Walk up from its enclosing .menu-item and open each ancestor accordion
        const activeItem = activeLink.closest('.menu-item');
        const parents = menu.getItemParentElements(activeItem) || [];
        parents.forEach(parentItem => {
            menu.show(parentItem);
        });
        }

        // 2d) Recalculate any dropdown positions
        KTMenu.updateDropdowns();
    }

    // 3) Wire up both normal loads and HTMX swaps
    document.addEventListener('DOMContentLoaded', () => {
        initMenus();
        syncActiveMenu();
    });

    document.addEventListener('htmx:load', () => {
        initMenus();
        syncActiveMenu();
    });
})();
