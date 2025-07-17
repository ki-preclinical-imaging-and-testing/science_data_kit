/**
 * Internationalization API for Science Data Kit
 * 
 * This module provides functions for fetching available languages and translations
 * from the server.
 */

/**
 * Fetch available languages from the server
 * 
 * @returns {Promise<Object>} A promise that resolves to an object mapping language codes to language names
 */
export const fetchAvailableLanguages = async () => {
  try {
    const response = await fetch('/api/i18n/languages');
    if (!response.ok) {
      throw new Error(`Failed to fetch languages: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching available languages:', error);
    // Return default languages if fetch fails
    return {
      en: 'English',
      es: 'Español',
      fr: 'Français',
      de: 'Deutsch',
      ja: '日本語'
    };
  }
};

/**
 * Fetch translations for a specific language
 * 
 * @param {string} language - Language code (e.g., 'en', 'es', 'fr')
 * @returns {Promise<Object>} A promise that resolves to an object mapping translation keys to translated text
 */
export const fetchTranslations = async (language) => {
  try {
    const response = await fetch(`/api/i18n/translations/${language}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch translations: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching translations for ${language}:`, error);
    // Return empty translations if fetch fails
    return {};
  }
};

/**
 * Set the current language
 * 
 * @param {string} language - Language code (e.g., 'en', 'es', 'fr')
 * @returns {Promise<void>} A promise that resolves when the language is set
 */
export const setLanguage = async (language) => {
  try {
    const response = await fetch('/api/i18n/language', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ language })
    });
    if (!response.ok) {
      throw new Error(`Failed to set language: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error setting language to ${language}:`, error);
    throw error;
  }
};