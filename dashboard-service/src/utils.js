// Utility functions for the dashboard

/**
 * Convert UTC timestamp to IST and format it
 * @param {string} utcTimestamp - ISO format timestamp in UTC
 * @param {boolean} includeDate - Include date in output
 * @returns {string} Formatted time in IST
 */
export const formatToIST = (utcTimestamp, includeDate = false) => {
  if (!utcTimestamp) return 'N/A';
  
  const date = new Date(utcTimestamp);
  
  // Convert to IST (UTC+5:30)
  const istDate = new Date(date.getTime() + (5.5 * 60 * 60 * 1000));
  
  if (includeDate) {
    return istDate.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  }
  
  return istDate.toLocaleTimeString('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
};

/**
 * Get current time in IST
 * @returns {string} Current time formatted in IST
 */
export const getCurrentIST = () => {
  return new Date().toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
};

/**
 * Format time for chart display (short format)
 * @param {string} utcTimestamp - ISO format timestamp in UTC
 * @returns {string} Short time format in IST (HH:mm)
 */
export const formatChartTime = (utcTimestamp) => {
  if (!utcTimestamp) return '';
  
  const date = new Date(utcTimestamp);
  const istDate = new Date(date.getTime() + (5.5 * 60 * 60 * 1000));
  
  return istDate.toLocaleTimeString('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });
};
