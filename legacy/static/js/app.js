document.addEventListener('DOMContentLoaded', function() {
    // Add any client-side interactivity here
    console.log('EEXI Calculator Loaded');

    const form = document.getElementById('eexiForm');
    
    // Mobile Menu Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            const icon = menuToggle.querySelector('i');
            if (navLinks.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!menuToggle.contains(e.target) && !navLinks.contains(e.target) && navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
                const icon = menuToggle.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });

        // Close menu when clicking a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                const icon = menuToggle.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            });
        });
    }

    if (form) {
        const shipTypeSelect = document.getElementById('ship_type');
        const dwtGroup = document.getElementById('dwt-group');
        const gtGroup = document.getElementById('gt-group');

        function updateCapacityFields() {
            const shipType = shipTypeSelect.value;
            if (shipType === 'ro_ro_pass' || shipType === 'cruise') {
                gtGroup.style.display = 'block';
                dwtGroup.style.display = 'none';
                document.getElementById('gt').setAttribute('required', 'required');
                document.getElementById('dwt').removeAttribute('required');
            } else {
                gtGroup.style.display = 'none';
                dwtGroup.style.display = 'block';
                document.getElementById('dwt').setAttribute('required', 'required');
                document.getElementById('gt').removeAttribute('required');
            }
        }

        if (shipTypeSelect) {
            shipTypeSelect.addEventListener('change', updateCapacityFields);
            // Run on load
            if (shipTypeSelect.value) {
                updateCapacityFields();
            } else {
                // Default: show both or hide both until type is selected?
                // For now, let's just show DWT as default
                gtGroup.style.display = 'none';
            }
        }

        form.addEventListener('submit', function(e) {
            // Set user's local time before submitting
            const now = new Date();
            const localTimeStr = now.getFullYear() + '-' + 
                               String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                               String(now.getDate()).padStart(2, '0') + ' ' + 
                               String(now.getHours()).padStart(2, '0') + ':' + 
                               String(now.getMinutes()).padStart(2, '0') + ':' + 
                               String(now.getSeconds()).padStart(2, '0');
            
            const timeInput = document.getElementById('user_local_time');
            if (timeInput) {
                timeInput.value = localTimeStr;
            }

            const dwt = document.getElementById('dwt').value;
            const gt = document.getElementById('gt').value;

            if (!dwt && !gt) {
                e.preventDefault();
                alert('Please provide either Deadweight (DWT) or Gross Tonnage (GT).');
            }
        });
    }
});
