import React, { useState, useRef, useEffect } from 'react';
import { FaTimes, FaChevronDown } from 'react-icons/fa';

const AutoCompleteWithBadges = ({ 
  label, 
  placeholder, 
  icon: Icon, 
  suggestions = [], 
  selectedItems = [], 
  onSelectionChange,
  maxItems = 5 
}) => {
  const [inputValue, setInputValue] = useState('');
  const [filteredSuggestions, setFilteredSuggestions] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  // Enhanced filtering function for better matching
  const getFilteredSuggestions = (input, suggestionsList, selectedItemsList) => {
    if (!input.trim() || !suggestionsList?.length) return [];
    
    const inputLower = input.toLowerCase().trim();
    
    // Multiple matching strategies for better results
    const matches = suggestionsList
      .filter(suggestion => !selectedItemsList.includes(suggestion))
      .map(suggestion => {
        const suggestionLower = suggestion.toLowerCase();
        let score = 0;
        
        // Exact match gets highest score
        if (suggestionLower === inputLower) {
          score = 100;
        }
        // Starts with input gets high score
        else if (suggestionLower.startsWith(inputLower)) {
          score = 90;
        }
        // Contains input gets medium score
        else if (suggestionLower.includes(inputLower)) {
          score = 70;
        }
        // Word boundary match gets medium-high score
        else if (new RegExp(`\\b${inputLower}`, 'i').test(suggestion)) {
          score = 80;
        }
        // Fuzzy match for partial words (like "St" matching "Stress")
        else if (inputLower.length >= 2) {
          const words = suggestionLower.split(/[\s,]+/);
          for (const word of words) {
            if (word.startsWith(inputLower)) {
              score = 85;
              break;
            }
          }
        }
        
        return { suggestion, score };
      })
      .filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, maxItems)
      .map(item => item.suggestion);
    
    return matches;
  };

  // Filter suggestions based on input and exclude already selected items
  useEffect(() => {
    console.log(`AutoComplete ${label} - Input value: "${inputValue}"`);
    console.log(`AutoComplete ${label} - Suggestions count: ${suggestions?.length || 0}`);
    console.log(`AutoComplete ${label} - Selected items:`, selectedItems);
    
    if (inputValue.trim()) {
      const filtered = getFilteredSuggestions(inputValue, suggestions, selectedItems);
      console.log(`AutoComplete ${label} - Filtered suggestions:`, filtered);
      setFilteredSuggestions(filtered);
      setIsOpen(filtered.length > 0);
    } else {
      setFilteredSuggestions([]);
      setIsOpen(false);
    }
    setHighlightedIndex(-1);
  }, [inputValue, suggestions, selectedItems, maxItems, label]);

  // Handle input change
  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  // Handle suggestion selection
  const handleSuggestionClick = (suggestion) => {
    if (!selectedItems.includes(suggestion)) {
      onSelectionChange([...selectedItems, suggestion]);
    }
    setInputValue('');
    setIsOpen(false);
    inputRef.current?.focus();
  };

  // Handle adding custom text
  const handleAddCustom = () => {
    const customText = inputValue.trim();
    if (customText && !selectedItems.includes(customText)) {
      onSelectionChange([...selectedItems, customText]);
    }
    setInputValue('');
    setIsOpen(false);
    inputRef.current?.focus();
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    switch (e.key) {
      case 'ArrowDown':
        if (isOpen) {
          e.preventDefault();
          const maxIndex = filteredSuggestions.length + (inputValue.trim() && !filteredSuggestions.includes(inputValue.trim()) ? 1 : 0) - 1;
          setHighlightedIndex(prev => 
            prev < maxIndex ? prev + 1 : prev
          );
        }
        break;
      case 'ArrowUp':
        if (isOpen) {
          e.preventDefault();
          setHighlightedIndex(prev => prev > 0 ? prev - 1 : -1);
        }
        break;
      case 'Enter':
        e.preventDefault();
        if (isOpen && highlightedIndex >= 0) {
          if (highlightedIndex < filteredSuggestions.length) {
            handleSuggestionClick(filteredSuggestions[highlightedIndex]);
          } else if (highlightedIndex === filteredSuggestions.length && inputValue.trim()) {
            // "Add custom" option is highlighted
            handleAddCustom();
          }
        } else if (inputValue.trim()) {
          // Add custom text if no suggestion is highlighted
          handleAddCustom();
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  // Remove selected item
  const removeItem = (itemToRemove) => {
    onSelectionChange(selectedItems.filter(item => item !== itemToRemove));
  };

  // Handle input focus
  const handleFocus = () => {
    if (filteredSuggestions.length > 0) {
      setIsOpen(true);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setHighlightedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="space-y-2">
      <label className="block text-sm font-bold text-black manga-text">
        {label}
      </label>
      
      <div className="relative" ref={dropdownRef}>
        {/* Input field */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {Icon && <Icon className="h-5 w-5 text-gray-500" />}
          </div>
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={handleFocus}
            placeholder={placeholder}
            className="w-full pl-10 pr-10 py-3 border-2 border-black rounded-lg bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent manga-text font-medium text-black placeholder-gray-500 shadow-lg"
          />
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <FaChevronDown className={`h-4 w-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </div>
        </div>

        {/* Selected items as badges */}
        {selectedItems.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {selectedItems.map((item, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 border border-blue-200 manga-text"
              >
                {item}
                <button
                  type="button"
                  onClick={() => removeItem(item)}
                  className="ml-2 inline-flex items-center justify-center w-4 h-4 rounded-full text-blue-600 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <FaTimes className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}

        {/* Dropdown suggestions */}
        {isOpen && (filteredSuggestions.length > 0 || inputValue.trim()) && (
          <div className="absolute z-10 w-full mt-1 bg-white border-2 border-black rounded-lg shadow-lg max-h-60 overflow-y-auto">
            {filteredSuggestions.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleSuggestionClick(suggestion)}
                className={`w-full px-4 py-3 text-left hover:bg-blue-50 focus:outline-none focus:bg-blue-50 manga-text font-medium ${
                  index === highlightedIndex ? 'bg-blue-50' : ''
                } ${index === 0 ? 'rounded-t-lg' : ''} ${
                  index === filteredSuggestions.length - 1 && !inputValue.trim() ? 'rounded-b-lg' : ''
                }`}
              >
                {suggestion}
              </button>
            ))}
            
            {/* Add custom option */}
            {inputValue.trim() && !filteredSuggestions.includes(inputValue.trim()) && (
              <button
                type="button"
                onClick={handleAddCustom}
                className={`w-full px-4 py-3 text-left hover:bg-green-50 focus:outline-none focus:bg-green-50 manga-text font-medium text-green-700 border-t border-gray-200 ${
                  highlightedIndex === filteredSuggestions.length ? 'bg-green-50' : ''
                } rounded-b-lg`}
              >
                + Add "{inputValue.trim()}"
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AutoCompleteWithBadges;
