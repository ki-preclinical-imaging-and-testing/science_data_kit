import React, { createContext, useState, useEffect } from 'react';
import { fetchAvailableLanguages, fetchTranslations } from '../api/i18nApi';

/**
 * Language Context for managing internationalization
 * 
 * This context provides language selection and translation functionality
 * for React components.
 */
export const LanguageContext = createContext();

/**
 * Language Provider Component
 * 
 * This component provides language context to its children.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 */
export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en');
  const [translations, setTranslations] = useState({});
  const [availableLanguages, setAvailableLanguages] = useState({ en: 'English' });
  
  // Fetch available languages on component mount
  useEffect(() => {
    fetchAvailableLanguages().then(setAvailableLanguages);
  }, []);
  
  // Fetch translations when language changes
  useEffect(() => {
    fetchTranslations(language).then(setTranslations);
  }, [language]);
  
  /**
   * Translate a key to the current language
   * 
   * @param {string} key - Translation key
   * @returns {string} Translated text
   */
  const translate = (key) => {
    return translations[key] || key;
  };
  
  return (
    <LanguageContext.Provider value={{ 
      language, 
      setLanguage, 
      translate, 
      availableLanguages 
    }}>
      {children}
    </LanguageContext.Provider>
  );
};