import React, { useContext } from 'react';
import { LanguageContext } from '../contexts/LanguageContext';

/**
 * Language Selector Component
 * 
 * This component displays a dropdown for selecting the language.
 * It uses the LanguageContext to get available languages and set the current language.
 * 
 * @param {Object} props - Component props
 * @param {string} props.className - CSS class name for the component
 */
const LanguageSelector = ({ className = 'language-selector' }) => {
  const { language, setLanguage, translate, availableLanguages } = useContext(LanguageContext);
  
  /**
   * Handle language change
   * 
   * @param {Event} e - Change event
   */
  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };
  
  return (
    <div className={className}>
      <label htmlFor="language-select">{translate('Language')}: </label>
      <select 
        id="language-select"
        value={language} 
        onChange={handleLanguageChange}
        aria-label={translate('Select language')}
      >
        {Object.entries(availableLanguages).map(([code, name]) => (
          <option key={code} value={code}>
            {name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSelector;