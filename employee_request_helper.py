﻿# employee_request_helper.py - Enhanced version with hybrid intent detection
import streamlit as st
import re
from datetime import datetime, timedelta
import openai
from config import OPENAI_API_KEY, OPENAI_MODEL
from odoo_connector import (
    get_available_leave_types, create_time_off_request, get_employee_leave_balance
)
from template_generator import (
    detect_template_intent, parse_embassy_details, generate_template,
    TEMPLATE_OPTIONS, COUNTRIES
)
from arabic_english_detection import (
    detect_time_off_intent_multilingual,
    detect_template_intent_multilingual,
    parse_arabic_date,
    convert_arabic_numerals,
    detect_exit_intent_multilingual
)
from typing import Optional

# Set up OpenAI for intent detection (optional)
openai.api_key = OPENAI_API_KEY

def detect_time_off_intent_nlp(query, use_openai=False):
    """
    Enhanced NLP-based detection of time-off intent
    
    Args:
        query: User's message
        use_openai: Whether to use OpenAI API for intent detection
        
    Returns:
        Tuple (is_time_off_request: bool, confidence: float)
    """
    query_lower = query.lower()
    
    # First, check for explicit non-requests (questions about balance, history, etc.)
    non_request_patterns = [
        r'how many days',
        r'how much (leave|time off|vacation)',
        r'check my (leave|balance|time off)',
        r'(leave|vacation|time off) balance',
        r'days (remaining|left|available)',
        r'did i take',
        r'have i taken',
        r'days i took',
        r'time off history',
        r'leave history',
        r'show my (leave|time off)',
        r'display my (leave|time off)',
        r'list my (leave|time off)',
        r'what is my (leave|vacation|time off)',
        r'do i have (leave|vacation|time off)'
    ]
    
    # If it matches non-request patterns, it's definitely not a request
    if any(re.search(pattern, query_lower) for pattern in non_request_patterns):
        return False, 0.0
    
    # Expanded patterns for time-off requests
    strong_request_patterns = [
        # Direct requests
        r'\b(i|I)(\s+would\s+like\s+to|\s+want\s+to|\s+need\s+to|\s+have\s+to|\s+must)?\s*(request|take|book|apply\s+for|get|have)\s+(some\s+)?(time\s*off|leave|vacation|holiday|pto|days?\s+off)\b',
        r'\b(request|requesting|apply\s+for|applying\s+for)\s+(time\s*off|leave|vacation|holiday|pto)\b',
        r'\b(take|taking|book|booking)\s+(time\s*off|leave|vacation|holiday|pto|days?\s+off)\b',
        r'\b(need|want|would\s+like)\s+(time\s*off|leave|vacation|holiday|pto|days?\s+off)\b',
        
        # Casual expressions
        r'\bi(\s+want\s+a|\s+need\s+a|\s+would\s+like\s+a)?\s*(vacation|holiday|break|day\s+off)\b',
        r'\bgoing\s+on\s+(vacation|leave|holiday)\b',
        r'\bi\'?m\s+(taking|planning)\s+(time\s*off|leave|vacation|holiday)\b',
        r'\bi\'?ll\s+be\s+(taking|out|off|away)\b',
        
        # Future tense indicators
        r'\bwill\s+be\s+(taking|out|off|away)\s+(on|from|between)\b',
        r'\bplan(?:ning)?\s+to\s+(take|be)\s+(off|away|out)\b',
        
        # Permission requests
        r'\b(can|may|could)\s+i\s+(take|have|get|request)\s+(time\s*off|leave|vacation|holiday|days?\s+off)\b',
        r'\bis\s+it\s+(possible|okay|fine)\s+(?:for\s+me\s+)?to\s+(take|request|have)\s+(time\s*off|leave|vacation)\b',
        
        # Specific day requests
        r'\b(sick|personal|annual|unpaid)\s+(day|leave|time\s*off)\b',
        r'\bcall(?:ing)?\s+in\s+sick\b',
        r'\bneed\s+.{0,20}\s+off\b',  # "need tomorrow off", "need next week off"
        
        # Informal variations
        r'\btime\s*off\s+request\b',
        r'\bleave\s+request\b',
        r'\bpto\s+request\b',
        r'\bout\s+of\s+office\b',
        r'\bwon\'?t\s+be\s+(in|at\s+work|available)\b'
    ]
    
    medium_confidence_patterns = [
        # Less direct but still indicative
        r'\b(vacation|holiday|leave)\s+(in|on|from|starting)\b',
        r'\boff\s+(work|from\s+work)\s+(on|from)\b',
        r'\bnot\s+(coming|be)\s+(in|to\s+work)\b',
        r'\baway\s+from\s+(work|office)\b',
        r'\btake\s+.{0,10}\s+off\b',  # "take Friday off"
        r'\bneed\s+.{0,10}\s+for\s+(personal|family|medical)\b',
        
        # Single word triggers in certain contexts
        r'\b(vacation|holiday|leave|pto|time\s*off)\b.*\b(date|when|tomorrow|next|this)\b',
        r'\b(tomorrow|next\s+week|next\s+month|june|july)\b.*\b(off|vacation|leave)\b'
    ]
    
    # Date-related patterns that suggest time off
    date_patterns = [
        r'\b(from|starting)\s+\d{1,2}[/-]\d{1,2}',
        r'\b(on|for)\s+\d{1,2}[/-]\d{1,2}',
        r'\b(june|july|august|september|october|november|december|january|february|march|april|may)\s+\d{1,2}',
        r'\bnext\s+(monday|tuesday|wednesday|thursday|friday|week|month)',
        r'\btomorrow\b',
        r'\b\d+\s+days?\b'
    ]
    
    # Calculate confidence based on pattern matches
    confidence = 0.0
    
    # Check strong patterns (high confidence)
    strong_match_count = sum(1 for pattern in strong_request_patterns if re.search(pattern, query_lower))
    if strong_match_count > 0:
        confidence = min(0.9, 0.7 + (0.1 * strong_match_count))
        return True, confidence
    
    # Check medium confidence patterns
    medium_match_count = sum(1 for pattern in medium_confidence_patterns if re.search(pattern, query_lower))
    date_match_count = sum(1 for pattern in date_patterns if re.search(pattern, query_lower))
    
    if medium_match_count > 0:
        confidence = 0.5 + (0.1 * medium_match_count) + (0.05 * date_match_count)
        if confidence >= 0.6:
            return True, confidence
    
    # If OpenAI is enabled and we're still unsure, use it for verification
    if use_openai and confidence < 0.6 and confidence > 0.3:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intent classifier. Determine if the user is requesting time off from work. Respond with only 'YES' or 'NO'."
                    },
                    {
                        "role": "user",
                        "content": f"Is this a request for time off/leave/vacation? Message: '{query}'"
                    }
                ],
                temperature=0.1,
                max_tokens=10
            )
            ai_response = response.choices[0].message.content.strip().upper() if response.choices[0].message.content else ""
            if "YES" in ai_response:
                return True, 0.7  # OpenAI confirmation gives moderate confidence
            else:
                return False, 0.0
        except Exception as e:
            print(f"OpenAI fallback intent check error: {e}")
            # If OpenAI fails, fall back to pattern matching result
            pass
    
    # Context-aware detection: check for vacation-related words with temporal context
    vacation_words = ['vacation', 'holiday', 'leave', 'off', 'away', 'pto', 'break']
    temporal_words = ['tomorrow', 'next', 'this', 'from', 'to', 'between', 'on', 'starting', 'until']
    
    vacation_present = any(word in query_lower for word in vacation_words)
    temporal_present = any(word in query_lower for word in temporal_words)
    
    if vacation_present and temporal_present:
        confidence = 0.5
        return True, confidence
    
    return False, 0.0

def detect_time_off_intent(query):
    """
    Hybrid approach to detect if the user is trying to request time off (English or Arabic)
    
    Args:
        query: User's message
        
    Returns:
        Boolean indicating if it's a time-off request
    """
    # Use the multilingual detection (Arabic + English)
    is_time_off, confidence = detect_time_off_intent_multilingual(query)
    
    # Store confidence in session state for debugging
    if 'debug_info' not in st.session_state:
        st.session_state.debug_info = {}
    st.session_state.debug_info['time_off_intent_confidence'] = confidence
    
    confidence_threshold = 0.5
    if confidence >= confidence_threshold:
        return True
    return False

def handle_employee_request(query, employee_data):
    """
    General handler for all employee requests (time-off, templates, etc.).
    This function will route to the appropriate specific handler.
    """
    st.session_state.active_workflow = 'employee_request'
    # Check for cancellation first
    if detect_exit_intent_multilingual(query):
        # Clear all relevant session states
        if 'time_off_request' in st.session_state:
            st.session_state.time_off_request = {}
        if 'template_request' in st.session_state:
            st.session_state.template_request = {}
        st.session_state.active_workflow = None
        return "Request cancelled. How else can I help?"

    # Check for time-off intent first
    if detect_time_off_intent(query) or st.session_state.get('time_off_request', {}).get('step'):
        return handle_time_off_request(query, employee_data)
    
    # Check for template request intent
    if detect_template_intent(query) or st.session_state.get('template_request', {}).get('step'):
        return handle_template_request(query, employee_data)
        
    # Fallback if no specific intent is detected, but this function was called
    # Try to handle as time-off by default, as it's the most common request
    return handle_time_off_request(query, employee_data)

# Keep all the other functions from the original file unchanged
def parse_single_date(date_str):
    """Helper function to parse a single date string with improved natural language support"""
    # ... (keep the original implementation)
    # Clean the date string
    date_str = date_str.strip().lower()
    
    # Remove common suffixes (st, nd, rd, th)
    date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    
    # Handle "X of month" format (e.g., "13 of june" -> "13 june")
    date_str = date_str.replace(' of ', ' ')
    
    # Get current date info
    today = datetime.now()
    current_year = today.year
    
    # Handle relative dates
    relative_dates = {
        'today': today,
        'tomorrow': today + timedelta(days=1),
        'yesterday': today - timedelta(days=1),
        'next monday': today + timedelta(days=(7 - today.weekday()) % 7 or 7),
        'next tuesday': today + timedelta(days=(8 - today.weekday()) % 7 or 7),
        'next wednesday': today + timedelta(days=(9 - today.weekday()) % 7 or 7),
        'next thursday': today + timedelta(days=(10 - today.weekday()) % 7 or 7),
        'next friday': today + timedelta(days=(11 - today.weekday()) % 7 or 7),
        'next saturday': today + timedelta(days=(12 - today.weekday()) % 7 or 7),
        'next sunday': today + timedelta(days=(13 - today.weekday()) % 7 or 7),
        'monday': today + timedelta(days=(0 - today.weekday()) % 7),
        'tuesday': today + timedelta(days=(1 - today.weekday()) % 7),
        'wednesday': today + timedelta(days=(2 - today.weekday()) % 7),
        'thursday': today + timedelta(days=(3 - today.weekday()) % 7),
        'friday': today + timedelta(days=(4 - today.weekday()) % 7),
        'saturday': today + timedelta(days=(5 - today.weekday()) % 7),
        'sunday': today + timedelta(days=(6 - today.weekday()) % 7),
    }
    
    # Check for relative dates
    for key, value in relative_dates.items():
        if key in date_str:
            return value.strftime('%Y-%m-%d')
    
    # Month names mapping
    months = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12
    }
    
    # Try to extract month name and day
    for month_name, month_num in months.items():
        # Pattern for "June 11", "11 June", "June 11, 2024"
        patterns = [
            rf'{month_name}\s+(\d{{1,2}})(?:\s*,?\s*(\d{{4}}))?',  # June 11 or June 11, 2024
            rf'(\d{{1,2}})\s+{month_name}(?:\s*,?\s*(\d{{4}}))?',  # 11 June or 11 June 2024
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                groups = match.groups()
                if pattern.startswith(r'(\d'):  # Day comes first
                    day = int(groups[0])
                    year = int(groups[1]) if groups[1] else current_year
                else:  # Month name comes first
                    day = int(groups[0])
                    year = int(groups[1]) if groups[1] else current_year
                
                try:
                    # If the date is in the past for current year, assume next year
                    parsed_date = datetime(year, month_num, day)
                    if parsed_date < today and year == current_year:
                        parsed_date = datetime(year + 1, month_num, day)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
    
    # Try standard date formats
    formats = [
        '%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y',
        '%m/%d', '%m-%d', '%d/%m/%Y', '%d-%m-%Y',
        '%d/%m', '%d-%m', '%Y-%m-%d', '%Y/%m/%d'
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            # If year is not in the format, add current year
            if '%Y' not in fmt and '%y' not in fmt:
                parsed = parsed.replace(year=current_year)
                # If the date is in the past, assume next year
                if parsed < today:
                    parsed = parsed.replace(year=current_year + 1)
            return parsed.strftime('%Y-%m-%d')
        except:
            continue
    
    return None

# ... (keep all other functions unchanged)
def parse_time_off_details(query):
    """
    Try to extract time-off details from the query with improved date parsing (Arabic + English)
    """
    details: dict[str, Optional[str]] = {
        'leave_type': None,
        'date_from': None,
        'date_to': None,
        'duration': None,
        'description': None
    }
    query_lower = query.lower()
    debug_log = {'input': query, 'steps': []}
    # Arabic leave type mapping
    arabic_leave_types = {
        'سنوية': 'annual', 'إجازة سنوية': 'annual', 'اجازة سنوية': 'annual',
        'مرضية': 'sick', 'إجازة مرضية': 'sick', 'اجازة مرضية': 'sick',
        'بدون راتب': 'unpaid', 'إجازة بدون راتب': 'unpaid', 'اجازة بدون راتب': 'unpaid',
        'شخصية': 'personal', 'إجازة شخصية': 'personal', 'اجازة شخصية': 'personal',
        'عارضة': 'casual', 'إجازة عارضة': 'casual', 'اجازة عارضة': 'casual',
    }
    for ar, en in arabic_leave_types.items():
        if ar in query:
            details['leave_type'] = en
            debug_log['steps'].append({'arabic_leave_type': en})
            break
    if not details['leave_type']:
        if 'sick' in query_lower:
            details['leave_type'] = 'sick'
        elif 'vacation' in query_lower or 'holiday' in query_lower or 'annual' in query_lower:
            details['leave_type'] = 'annual'
        elif 'personal' in query_lower:
            details['leave_type'] = 'personal'
        elif 'unpaid' in query_lower:
            details['leave_type'] = 'unpaid'
    is_arabic = any('\u0600' <= c <= '\u06FF' for c in query)
    if is_arabic:
        date = parse_arabic_date(query)
        if date:
            details['date_from'] = date
            details['date_to'] = date
            debug_log['steps'].append({'arabic_date': date})
            st.session_state.debug_info['date_parsing'] = debug_log
            return details
        query = convert_arabic_numerals(query)
    text_for_parsing = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', query_lower)

    # Improved date range regex: handles 'from June 29 to 30', 'from 29/6 to 30/6', 'June 29th till the 30th', etc.
    date_range_patterns = [
        # from June 29 to 30, from June 29th till the 30th
        r'(?:from\s+)?(\w+\s+\d{1,2})(?:st|nd|rd|th)?\s*(?:to|till|until|through|-|–)\s*(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?',
        # from 29/6 to 30/6 or 29-6 to 30-6
        r'(?:from\s+)?(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\s*(?:to|till|until|through|-|–)\s*(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)',
        # June 29 to June 30
        r'(?:from\s+)?(\w+\s+\d{1,2})(?:st|nd|rd|th)?\s*(?:to|till|until|through|-|–)\s*(\w+\s+\d{1,2})(?:st|nd|rd|th)?',
        # 29 June to 30 June
        r'(?:from\s+)?(\d{1,2}\s+\w+)(?:st|nd|rd|th)?\s*(?:to|till|until|through|-|–)\s*(\d{1,2}\s+\w+)(?:st|nd|rd|th)?',
        # 29/6 to 30
        r'(?:from\s+)?(\d{1,2}[/-]\d{1,2})(?:[/-]\d{2,4})?\s*(?:to|till|until|through|-|–)\s*(\d{1,2})(?:st|nd|rd|th)?',
    ]
    for pattern in date_range_patterns:
        match = re.search(pattern, text_for_parsing, re.IGNORECASE)
        if match:
            date_from_str = match.group(1).strip()
            date_to_str = match.group(2).strip()
            debug_log['steps'].append({'matched_pattern': pattern, 'groups': [date_from_str, date_to_str]})
            # If the second date is just a day, try to infer the month from the first
            if re.match(r'^\d{1,2}$', date_to_str):
                month_match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)', date_from_str, re.IGNORECASE)
                if month_match:
                    month = month_match.group(1)
                    date_to_str = f"{date_to_str} {month}"
            parsed_from = parse_single_date(date_from_str)
            parsed_to = parse_single_date(date_to_str)
            debug_log['steps'].append({'parsed_from': parsed_from, 'parsed_to': parsed_to})
            if parsed_from and parsed_to:
                details['date_from'] = parsed_from
                details['date_to'] = parsed_to
                st.session_state.debug_info['date_parsing'] = debug_log
                return details
            else:
                debug_log['steps'].append({'range_parse_failed': True})
    # Fallback to original range pattern
    date_range_pattern = r'(?:from\s+)?(\d{1,2}(?:\s+of)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)|(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\s+\d{1,2}|\d{1,2}/\d{1,2}(?:/\d{2,4})?)\s+(?:to|till|until|through|-|–)\s+(?:the\s+)?(\d{1,2}(?:\s+of)?\s*(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)?|(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\s+\d{1,2}|\d{1,2}/\d{1,2}(?:/\d{2,4})?)'
    match = re.search(date_range_pattern, text_for_parsing, re.IGNORECASE)
    if match:
        date_from_str = match.group(1).strip()
        date_to_str = match.group(2).strip()
        date_from_str = date_from_str.replace(' of ', ' ')
        date_to_str = date_to_str.replace(' of ', ' ')
        if re.match(r'^\d{1,2}$', date_to_str):
            month_match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)', date_from_str, re.IGNORECASE)
            if month_match:
                month = month_match.group(1)
                date_to_str = f"{date_to_str} {month}"
        parsed_from = parse_single_date(date_from_str)
        parsed_to = parse_single_date(date_to_str)
        debug_log['steps'].append({'fallback_range': [date_from_str, date_to_str], 'parsed_from': parsed_from, 'parsed_to': parsed_to})
        if parsed_from and parsed_to:
            details['date_from'] = parsed_from
            details['date_to'] = parsed_to
            st.session_state.debug_info['date_parsing'] = debug_log
            return details
        else:
            debug_log['steps'].append({'fallback_range_parse_failed': True})
    # Duration pattern
    duration_match = re.search(r'(\d+)\s*days?\s*(?:starting|from|beginning)?\s*(.+?)(?:\.|,|$)', text_for_parsing)
    if duration_match:
        days = int(duration_match.group(1))
        start_date_str = duration_match.group(2).strip()
        parsed_start = parse_single_date(start_date_str)
        debug_log['steps'].append({'duration': days, 'start_date_str': start_date_str, 'parsed_start': parsed_start})
        if parsed_start:
            details['date_from'] = parsed_start
            start_dt = datetime.strptime(parsed_start, '%Y-%m-%d')
            end_dt = start_dt + timedelta(days=days - 1)
            details['date_to'] = end_dt.strftime('%Y-%m-%d')
            st.session_state.debug_info['date_parsing'] = debug_log
            return details
    # Single date: tomorrow, today, etc.
    if 'tomorrow' in text_for_parsing:
        tomorrow = datetime.now() + timedelta(days=1)
        details['date_from'] = tomorrow.strftime('%Y-%m-%d')
        details['date_to'] = details['date_from']
        debug_log['steps'].append({'single_date': 'tomorrow', 'parsed': details['date_from']})
        st.session_state.debug_info['date_parsing'] = debug_log
        return details
    elif 'today' in text_for_parsing:
        today = datetime.now()
        details['date_from'] = today.strftime('%Y-%m-%d')
        details['date_to'] = details['date_from']
        debug_log['steps'].append({'single_date': 'today', 'parsed': details['date_from']})
        st.session_state.debug_info['date_parsing'] = debug_log
        return details
    # Single month + day
    single_date_match = re.search(r'(\d{1,2})\s+(?:of\s+)?(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)|(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\s+(\d{1,2})', text_for_parsing, re.IGNORECASE)
    if single_date_match:
        date_str = single_date_match.group(0).replace(' of ', ' ')
        parsed_date = parse_single_date(date_str)
        debug_log['steps'].append({'single_date_match': date_str, 'parsed': parsed_date})
        if parsed_date:
            details['date_from'] = parsed_date
            details['date_to'] = parsed_date
            duration_after = re.search(r'for\s+(\d+)\s*days?', text_for_parsing[single_date_match.end():])
            if duration_after:
                days = int(duration_after.group(1))
                from_dt = datetime.strptime(parsed_date, '%Y-%m-%d')
                to_dt = from_dt + timedelta(days=days - 1)
                details['date_to'] = to_dt.strftime('%Y-%m-%d')
            st.session_state.debug_info['date_parsing'] = debug_log
            return details
    debug_log['steps'].append({'parse_failed': True})
    st.session_state.debug_info['date_parsing'] = debug_log
    return details

def handle_time_off_request(query, employee_data):
    """
    Handle the time-off request flow
    
    Args:
        query: User's message
        employee_data: Employee data dictionary
        
    Returns:
        Response message
    """
    # Check if we have pending time-off request in session
    if 'time_off_request' not in st.session_state:
        st.session_state.time_off_request = {}
    
    request_data = st.session_state.time_off_request
    employee_id = employee_data.get('id')
    
    # If this is a new request, try to parse details from the query
    if not request_data:
        parsed_details = parse_time_off_details(query)
        request_data.update(parsed_details)

    # If dates are missing, try to parse them from the current input
    if (not request_data.get('date_from') or not request_data.get('date_to')):
        parsed_details = parse_time_off_details(query)
        # Only update if the fields are missing and the parser found them
        if not request_data.get('date_from') and parsed_details.get('date_from'):
            request_data['date_from'] = parsed_details['date_from']
        if not request_data.get('date_to') and parsed_details.get('date_to'):
            request_data['date_to'] = parsed_details['date_to']
    
    # Check what information we still need
    missing_info = []
    
    # Get available leave types
    leave_types = get_available_leave_types()
    
    # Filter to only show Annual, Sick, and Unpaid leave types
    allowed_types = ['annual', 'sick', 'unpaid']
    filtered_leave_types = []
    
    for lt in leave_types:
        lt_name_lower = lt['name'].lower()
        # Check if any of our allowed types are in the leave type name
        for allowed in allowed_types:
            if allowed in lt_name_lower:
                filtered_leave_types.append(lt)
                break
    
    # If we couldn't find the filtered types, use all types
    if not filtered_leave_types:
        filtered_leave_types = leave_types
    
    # Create a mapping of leave types for easier matching
    leave_type_map = {}
    for lt in filtered_leave_types:
        # Create multiple keys for better matching
        name_lower = lt['name'].lower()
        leave_type_map[name_lower] = lt
        
        # Also add simplified keys
        if 'annual' in name_lower:
            leave_type_map['annual'] = lt
            leave_type_map['vacation'] = lt
            leave_type_map['pto'] = lt
        elif 'sick' in name_lower:
            leave_type_map['sick'] = lt
            leave_type_map['sick leave'] = lt
            leave_type_map['sick time'] = lt
        elif 'unpaid' in name_lower:
            leave_type_map['unpaid'] = lt
            leave_type_map['unpaid leave'] = lt
            leave_type_map['lwop'] = lt
    
    # Check leave type
    if not request_data.get('leave_type_id'):
        # Try to match user input with leave types
        query_lower = query.lower().strip()
        is_arabic = any('\u0600' <= c <= '\u06FF' for c in query)
        # First check if the query matches any leave type directly
        if query_lower in leave_type_map:
            lt = leave_type_map[query_lower]
            request_data['leave_type_id'] = lt['id']
            request_data['leave_type_name'] = lt['name']
        else:
            # Check if any leave type key is in the query
            for key, lt in leave_type_map.items():
                if key in query_lower or query_lower in key:
                    request_data['leave_type_id'] = lt['id']
                    request_data['leave_type_name'] = lt['name']
                    break
        # If still not found, check the parsed leave type
        if not request_data.get('leave_type_id') and request_data.get('leave_type'):
            parsed_type = request_data['leave_type']
            # If Arabic, match mapped English type to Odoo leave type names
            if is_arabic:
                for lt in filtered_leave_types:
                    if parsed_type in lt['name'].lower():
                        request_data['leave_type_id'] = lt['id']
                        request_data['leave_type_name'] = lt['name']
                        break
            # Also try fallback for English
            if not request_data.get('leave_type_id'):
                for key, lt in leave_type_map.items():
                    if parsed_type in key:
                        request_data['leave_type_id'] = lt['id']
                        request_data['leave_type_name'] = lt['name']
                        break
        if not request_data.get('leave_type_id'):
            missing_info.append('leave_type')
    
    # Check dates
    if not request_data.get('date_from'):
        missing_info.append('date_from')
    if not request_data.get('date_to'):
        missing_info.append('date_to')
    
    # Store the updated request data
    st.session_state.time_off_request = request_data
    
    # Debug logging
    if 'debug_info' not in st.session_state:
        st.session_state.debug_info = {}
    st.session_state.debug_info['time_off_request'] = {
        'current_state': request_data,
        'missing_info': missing_info,
        'query': query
    }
    
    # Add exit/cancel detection for Arabic
    if detect_exit_intent_multilingual(query):
        st.session_state.time_off_request = {}
        st.session_state.active_workflow = None
        return "تم إلغاء عملية طلب الإجازة. يمكنك البدء من جديد أو طلب مساعدة أخرى."
    
    # If we have all information, process the request
    if not missing_info:
        # Get the leave balance for this type
        balance = get_employee_leave_balance(employee_id, request_data['leave_type_id'])
        
        # Calculate requested days
        date_from = datetime.strptime(request_data['date_from'], '%Y-%m-%d')
        date_to = datetime.strptime(request_data['date_to'], '%Y-%m-%d')
        requested_days = (date_to - date_from).days + 1
        
        # Check if enough balance (only for non-unpaid leave)
        if 'unpaid' not in request_data['leave_type_name'].lower() and balance['available'] < requested_days:
            # Clear the request data
            st.session_state.time_off_request = {}
            st.session_state.active_workflow = None
            return f"""I see you want to request {requested_days} days of {request_data['leave_type_name']}, but you only have {balance['available']} days available.

Your current balance:
- Available: {balance['available']} days
- Already used: {balance['used']} days
- Total allocated: {balance['allocated']} days

Would you like to request a different number of days or check another leave type?

💡 *Type "cancel" to exit this process.*"""
        
        # Create the time-off request
        result = create_time_off_request(
            employee_id,
            request_data['leave_type_id'],
            request_data['date_from'],
            request_data['date_to'],
            request_data.get('description', f"Time off request via chatbot")
        )
        
        # Clear the request data
        st.session_state.time_off_request = {}
        st.session_state.active_workflow = None
        
        if result['success']:
            balance_info = ""
            if 'unpaid' not in request_data['leave_type_name'].lower():
                balance_info = f"\n- Remaining balance: {balance['available'] - requested_days} days"
            
            return f"""✅ {result['message']}

Details of your request:
- Type: {request_data['leave_type_name']}
- From: {request_data['date_from']}
- To: {request_data['date_to']}
- Days: {requested_days}{balance_info}

Your request has been submitted and is pending approval from your manager."""
        else:
            return f"""❌ {result['message']}

Please check the dates and try again, or contact HR for assistance.

💡 *Type "cancel" to exit this process.*"""
    
    # If we need more information, ask for it
    else:
        is_arabic = any('\u0600' <= c <= '\u06FF' for c in query)
        if 'leave_type' in missing_info:
            leave_type_list = "\n".join([f"- {lt['name']}" for lt in filtered_leave_types])
            if not filtered_leave_types:
                leave_type_list = "- Annual Leave\n- Sick Leave\n- Unpaid Leave"
            if is_arabic:
                return f"""يرجى تحديد نوع الإجازة التي ترغب بها (على سبيل المثال: إجازة سنوية، إجازة مرضية، إجازة بدون راتب):\n\n{leave_type_list}\n\nاكتب نوع الإجازة أدناه.\n\n💡 اكتب 'إلغاء' في أي وقت للخروج من هذه العملية."""
            else:
                return f"""I'd be happy to help you request time off! What type of leave would you like to request?\n\nAvailable leave types:\n{leave_type_list}\n\nJust type the leave type (e.g., \"annual\", \"sick\", or \"unpaid\").\n\n💡 *Type \"cancel\" at any time to exit this process.*"""
        elif 'date_from' in missing_info or 'date_to' in missing_info:
            if is_arabic:
                return f"يرجى تحديد تاريخ بدء الإجازة وتاريخ الانتهاء (مثال: ١٥ يونيو أو غداً أو من ١٥ يونيو إلى ٢٠ يونيو).\n💡 اكتب 'إلغاء' في أي وقت للخروج من هذه العملية."
            else:
                return f"Great! You want to request {request_data.get('leave_type_name', 'time off')}. \n\nNow, please provide the dates:\n- What date would you like to start your time off?\n- What date would you like to return?\n\nYou can say something like:\n- \"from 3/15 to 3/17\"\n- \"3/15 to 3/17\"  \n- \"from March 15 to March 17\"\n- \"tomorrow\" (for a single day)\n- \"from June 1st till the 2nd\"\n- \"13 of june till 14th\"\n- \"next Monday to Friday\"\n\nPlease provide your dates.\n\n💡 *Type \"cancel\" at any time to exit this process.*"

def handle_template_request(query, employee_data):
    """
    Handle template generation requests (Arabic or English intent)
    
    Args:
        query: User's message
        employee_data: Employee data dictionary
        
    Returns:
        Response message
    """
    # Check if we have pending template request in session
    if 'template_request' not in st.session_state:
        st.session_state.template_request = {}
    
    request_data = st.session_state.template_request
    
    # Detect template type if not already set
    if not request_data.get('template_type'):
        template_type = detect_template_intent_multilingual(query)
        if template_type and template_type != 'general_template_request':
            request_data['template_type'] = template_type
    
    # If embassy letter, check for additional details
    if request_data.get('template_type') == 'employment_letter_embassy':
        if not request_data.get('embassy_details'):
            # Parse embassy details from query
            embassy_details = parse_embassy_details(query)
            request_data['embassy_details'] = embassy_details
        else:
            # Update embassy details with new information from query
            new_details = parse_embassy_details(query)
            if new_details.get('country'):
                request_data['embassy_details']['country'] = new_details['country']
            if new_details.get('start_date'):
                request_data['embassy_details']['start_date'] = new_details['start_date']
            if new_details.get('end_date'):
                request_data['embassy_details']['end_date'] = new_details['end_date']
        
        # Check if we need more information
        embassy_details = request_data.get('embassy_details', {})
        missing_info = []
        
        if not embassy_details.get('country'):
            missing_info.append('country')
        if not embassy_details.get('start_date'):
            missing_info.append('start_date')
        if not embassy_details.get('end_date'):
            missing_info.append('end_date')
        
        # Store updated request data
        st.session_state.template_request = request_data
        
        if missing_info:
            if 'country' in missing_info:
                # Show country selection
                countries_list = ", ".join(COUNTRIES[:10]) + "..."
                return f"""I'll help you generate an employment letter for embassy/visa purposes. 

Which country are you traveling to? Please specify the country name.

Some examples: {countries_list}

💡 *Type "cancel" to exit this process.*"""
            
            elif 'start_date' in missing_info or 'end_date' in missing_info:
                # Try to parse dates one more time
                parsed_dates = parse_time_off_details(query)  # Reuse the date parsing logic
                if parsed_dates.get('date_from'):
                    request_data['embassy_details']['start_date'] = parsed_dates['date_from']
                if parsed_dates.get('date_to'):
                    request_data['embassy_details']['end_date'] = parsed_dates['date_to']
                
                # Update session state
                st.session_state.template_request = request_data
                
                # Check again if we have all info now
                embassy_details = request_data.get('embassy_details', {})
                if embassy_details.get('start_date') and embassy_details.get('end_date'):
                    # Continue with generation
                    pass
                else:
                    return f"""For the employment letter to {embassy_details.get('country', 'the embassy')}, I need your travel dates.

Please provide:
- Start date of your travel
- End date of your travel

You can say something like "from March 15 to March 25" or "3/15 to 3/25".

💡 *Type "cancel" to exit this process.*"""
    
    # If we have all necessary information, generate the template
    template_type = request_data.get('template_type')
    
    if template_type and template_type != 'general_template_request':
        # Generate the template
        embassy_details = request_data.get('embassy_details') if template_type == 'employment_letter_embassy' else None
        
        result = generate_template(template_type, employee_data, embassy_details)
        
        # Clear the request data
        st.session_state.template_request = {}
        st.session_state.active_workflow = None
        
        if result:
            doc_bytes, filename = result
            
            # Store in session state for download
            st.session_state['template_bytes'] = doc_bytes
            st.session_state['template_filename'] = filename
            
            template_info = TEMPLATE_OPTIONS.get(template_type, {})
            
            response = f"""✅ I've generated your {template_info.get('name', 'document')}!

📄 **Document Details:**
- Employee: {employee_data.get('name')}
- Type: {template_info.get('description', 'Employment document')}"""
            
            if embassy_details:
                response += f"""
- Country: {embassy_details.get('country')}
- Travel dates: {embassy_details.get('start_date')} to {embassy_details.get('end_date')}"""
            
            response += f"""

The document has been prepared and is ready for download. Click the download button below to save it.

**Note:** Please review the document before submitting it. If you need any changes, let me know!

[DOWNLOAD_BUTTON_PLACEHOLDER]"""
            
            return response
        else:
            # Check debug info for error details
            debug_info = st.session_state.get('debug_info', {})
            template_error = debug_info.get('template_error', 'Unknown error')
            
            return f"""❌ I'm sorry, I couldn't generate the template. 

Error: {template_error}

This might be because:
1. The template file is not available at the expected location
2. There was an error processing your information

Please ensure the template files are located at:
C:\\Users\\Geeks\\source\\repos\\CSTemplates\\

Or contact IT support for assistance.

💡 *Type "cancel" to return to normal chat.*"""
    
    # If no specific template detected, show options
    else:
        template_list = "\n".join([f"- **{info['name']}**: {info['description']}" for info in TEMPLATE_OPTIONS.values()])
        
        return f"""I can help you generate various employment documents. Here are the available templates:

{template_list}

Which type of document would you like me to generate for you?

You can ask for:
- "Employment letter" (standard English version)
- "Employment letter in Arabic"
- "Embassy letter for [country name]"
- "Experience certificate"

Just let me know which one you need!

💡 *Type "cancel" to exit this process.*"""

    # Add exit/cancel detection for Arabic
    if detect_exit_intent_multilingual(query):
        st.session_state.template_request = {}
        st.session_state.active_workflow = None
        return "تم إلغاء عملية إنشاء المستند. يمكنك البدء من جديد أو طلب مساعدة أخرى."