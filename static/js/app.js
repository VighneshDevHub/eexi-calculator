document.addEventListener('DOMContentLoaded', function() {
    // Add any client-side interactivity here
    console.log('EEXI Calculator Loaded');

    const form = document.getElementById('eexiForm');
    if (form) {
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
