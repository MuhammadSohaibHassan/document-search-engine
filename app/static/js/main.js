// Main JavaScript file for Document Search Engine

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Set up CSRF token for AJAX requests
    // Get the CSRF token from the meta tag
    var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Set up jQuery AJAX with CSRF token for all requests
    if (typeof $.ajaxSetup === 'function') {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                }
            }
        });
    }
    
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle document delete confirmations
    const deleteButtons = document.querySelectorAll('.delete-document-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Handle user delete confirmations
    const deleteUserButtons = document.querySelectorAll('.delete-user-btn');
    deleteUserButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this user? All their documents will also be deleted. This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Initialize Pakistan Standard Time display
    initializePakistanTimeDisplay();
    
    // Format search result timestamps
    formatSearchResultTimestamps();
});

/**
 * Convert local device time to Pakistan Standard Time
 * Pakistan is UTC+5
 * @returns {Date} Date object representing current Pakistan time
 */
function getPakistanTime() {
    // Get current time from user's device
    const localTime = new Date();
    
    // Get UTC time by adjusting for the local timezone offset
    const utcTime = new Date(localTime.getTime() + (localTime.getTimezoneOffset() * 60000));
    
    // Calculate Pakistan time by adding 5 hours to UTC
    const pakistanTime = new Date(utcTime.getTime() + (5 * 60 * 60000));
    
    return pakistanTime;
}

/**
 * Format a date in Pakistan Standard Time format
 * @param {Date} date - Date to format
 * @returns {string} Formatted date string
 */
function formatPakistanTime(date) {
    // Define month names
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    
    const month = months[date.getMonth()];
    const day = date.getDate();
    const year = date.getFullYear();
    
    // Get hours in 12-hour format
    let hours = date.getHours();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // Convert hour '0' to '12'
    
    // Ensure minutes have leading zero if needed
    const minutes = date.getMinutes().toString().padStart(2, '0');
    
    return `${month} ${day}, ${year} ${hours}:${minutes} ${ampm} (PKT)`;
}

/**
 * Update the displayed time in the client's timezone
 */
function updateCurrentPakistanTime() {
    const timeElements = document.querySelectorAll('.pakistan-time');
    const pakistanTime = getPakistanTime();
    const timeString = formatPakistanTime(pakistanTime);
    
    timeElements.forEach(element => {
        element.textContent = timeString;
    });
}

/**
 * Format timestamps in search results to Pakistan time
 */
function formatSearchResultTimestamps() {
    console.log("Formatting search result timestamps...");
    const timestamps = document.querySelectorAll('.formatted-timestamp');
    
    timestamps.forEach((element, index) => {
        try {
            // First check if there's a raw timestamp data attribute
            const rawTimestamp = element.getAttribute('data-raw-timestamp');
            
            // Get the original timestamp text
            const timestampText = element.textContent.trim();
            console.log(`Original timestamp [${index}]: ${timestampText}`);
            
            // Parse the timestamp - first try to see if it's already in PKT format
            if (timestampText.endsWith('(PKT)')) {
                console.log(`Timestamp [${index}] already in PKT format`);
                return;
            }
            
            // Handle format: "MMM DD, YYYY HH:MM AM/PM (PKT)"
            // Example: "Feb 15, 2023, 10:30 AM (PKT)"
            let date;
            
            // Use the raw timestamp if available
            if (rawTimestamp && rawTimestamp !== timestampText) {
                console.log(`Using raw timestamp [${index}]: ${rawTimestamp}`);
                
                // Check if the raw timestamp already has PKT format
                if (rawTimestamp.endsWith('(PKT)')) {
                    element.textContent = rawTimestamp;
                    console.log(`Raw timestamp [${index}] already in PKT format`);
                    return;
                }
                
                // Try to parse the raw timestamp
                try {
                    // If the raw timestamp is in MMM DD, YYYY HH:MM AM/PM format
                    if (/[A-Za-z]{3}\s+\d{1,2},\s+\d{4}\s+\d{1,2}:\d{2}\s+[AP]M/.test(rawTimestamp)) {
                        // Extract parts
                        const match = /([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})\s+(\d{1,2}):(\d{2})\s+([AP]M)/.exec(rawTimestamp);
                        if (match) {
                            const [_, month, day, year, hour, minute, ampm] = match;
                            const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                            const monthIndex = months.indexOf(month);
                            
                            if (monthIndex >= 0) {
                                // Convert hour to 24-hour format
                                let hour24 = parseInt(hour);
                                if (ampm === 'PM' && hour24 < 12) hour24 += 12;
                                if (ampm === 'AM' && hour24 === 12) hour24 = 0;
                                
                                date = new Date(year, monthIndex, parseInt(day), hour24, parseInt(minute));
                            }
                        }
                    } else {
                        // Try direct parsing
                        date = new Date(rawTimestamp);
                    }
                    
                    if (date && !isNaN(date.getTime())) {
                        console.log(`Parsed raw timestamp [${index}] to: ${date.toString()}`);
                    } else {
                        console.log(`Failed to parse raw timestamp [${index}]`);
                    }
                } catch (e) {
                    console.error(`Error parsing raw timestamp [${index}]:`, e);
                }
            }
            
            // If we couldn't parse the raw timestamp, try the displayed text
            if (!date || isNaN(date.getTime())) {
                // Try different regex patterns to handle various server-side formats
                
                // First pattern: "MMM DD, YYYY HH:MM AM/PM"
                const pattern1 = /([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})\s+(\d{1,2}):(\d{2})\s+([AP]M)/;
                // Second pattern: "MMM DD, YYYY HH:MM AM/PM (PKT)" (already formatted)
                const pattern2 = /([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})\s+(\d{1,2}):(\d{2})\s+([AP]M)\s+\(PKT\)/;
                // Third pattern: "MMM DD, YYYY, HH:MM AM/PM" (with comma after year)
                const pattern3 = /([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4}),\s+(\d{1,2}):(\d{2})\s+([AP]M)/;
                
                let match = pattern1.exec(timestampText) || pattern3.exec(timestampText);
                
                if (pattern2.test(timestampText)) {
                    console.log(`Timestamp [${index}] already in PKT format (matched pattern2)`);
                    return;
                }
                
                if (match) {
                    const [_, month, day, year, hour, minute, ampm] = match;
                    
                    // Convert to a standard date string that JavaScript can parse
                    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                    const monthIndex = months.indexOf(month);
                    
                    if (monthIndex >= 0) {
                        // Convert hour to 24-hour format
                        let hour24 = parseInt(hour);
                        if (ampm === 'PM' && hour24 < 12) hour24 += 12;
                        if (ampm === 'AM' && hour24 === 12) hour24 = 0;
                        
                        // Create a date object
                        date = new Date(year, monthIndex, parseInt(day), hour24, parseInt(minute));
                        console.log(`Parsed date [${index}]: ${date.toString()}`);
                    }
                } else {
                    // Try a last resort - direct parsing (works with some formats)
                    try {
                        date = new Date(timestampText);
                        if (isNaN(date.getTime())) {
                            console.log(`Failed to parse timestamp [${index}]: ${timestampText}`);
                            return; // Invalid date
                        }
                        console.log(`Direct parsed date [${index}]: ${date.toString()}`);
                    } catch (e) {
                        console.log(`Error parsing timestamp [${index}]: ${e.message}`);
                        return;
                    }
                }
            }
            
            if (date && !isNaN(date.getTime())) {
                // Now convert to Pakistan time (UTC+5)
                // First get UTC time
                const utcTime = new Date(date.getTime() + (date.getTimezoneOffset() * 60000));
                // Then add 5 hours for Pakistan time
                const pakistanTime = new Date(utcTime.getTime() + (5 * 60 * 60000));
                
                // Format the date
                const formattedTime = formatPakistanTime(pakistanTime);
                element.textContent = formattedTime;
                console.log(`Converted timestamp [${index}] to: ${formattedTime}`);
            } else {
                console.log(`Could not parse timestamp [${index}]: ${timestampText}`);
            }
        } catch (e) {
            console.error(`Error formatting timestamp [${index}]:`, e);
        }
    });
}

/**
 * Convert all timestamp elements to client-based Pakistan time
 */
function convertTimestamps() {
    // Look for elements with data-timestamp attribute
    const timestampElements = document.querySelectorAll('[data-timestamp]');
    
    timestampElements.forEach(element => {
        try {
            // Get the original timestamp in ISO format
            const timestamp = element.getAttribute('data-timestamp');
            const date = new Date(timestamp);
            
            if (!isNaN(date.getTime())) {
                // Valid date - format it in Pakistan time
                element.textContent = formatPakistanTime(date);
            }
        } catch (e) {
            console.error('Error converting timestamp:', e);
        }
    });
}

/**
 * Initialize all time-related displays
 */
function initializePakistanTimeDisplay() {
    // Update current time
    updateCurrentPakistanTime();
    
    // Update timestamps
    convertTimestamps();
    
    // Update current time every minute
    setInterval(updateCurrentPakistanTime, 60000);
} 