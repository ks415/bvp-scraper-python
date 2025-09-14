"""
Program scraper for race programs and boat/racer information.
"""

import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

from ..base_scraper import BaseScraper


class ProgramScraper(BaseScraper):
    """Scraper for race programs and participant information."""
    
    def scrape(self, race_date: Union[date, datetime, str], 
               race_stadium_number: int, race_number: int) -> Dict[str, Any]:
        """
        Scrape race program data.
        
        Args:
            race_date: Race date
            race_stadium_number: Stadium number (1-24)
            race_number: Race number (1-12)
            
        Returns:
            Dictionary containing race program data
        """
        parsed_date = self._parse_date(race_date)
        
        # Build scraper URL
        url = (f"{self.base_url}/owpc/pc/race/racelist"
               f"?hd={parsed_date.strftime('%Y%m%d')}"
               f"&jcd={race_stadium_number:02d}"
               f"&rno={race_number}")
        
        soup = self.request_and_parse(url)
        
        # Determine base level from page structure
        self.base_level = 0
        level_element = soup.select_one('body main div div div div:nth-child(2) div:nth-child(3) ul li')
        if level_element:
            self.base_level = 1
        
        # Extract race information
        race_data = self._scrape_race_info(soup, parsed_date, race_stadium_number, 
                                           race_number)
        
        # Extract boat and racer information
        boats_data = self._scrape_boats(soup)
        
        response = {**race_data, **boats_data}
        return response
    
    def _scrape_race_info(self, soup, race_date: date, race_stadium_number: int,
                          race_number: int) -> Dict[str, Any]:
        """Extract basic race information."""
        
        # CSS selectors for race information
        race_grade_selector = 'body main div div div div:nth-child(1) div div:nth-child(2)'
        race_title_selector = 'body main div div div div:nth-child(1) div div:nth-child(2) h2'
        race_subtitle_distance_selector = f'body main div div div div:nth-child(2) div:nth-child({self.base_level + 3}) h3'
        race_deadline_selector = f'body main div div div div:nth-child(2) div:nth-child(2) table tbody tr:nth-child(1) td:nth-child({race_number + 1})'
        
        # Extract data
        race_grade_number = self.filter_xpath_for_grade_number(soup, race_grade_selector)
        race_title = self.filter_xpath_text(soup, race_title_selector)
        race_subtitle_distance = self.filter_xpath_text(soup, race_subtitle_distance_selector)
        race_deadline = self.filter_xpath_text(soup, race_deadline_selector)
        
        # Parse race closed time
        race_closed_at = None
        if race_deadline:
            try:
                from datetime import datetime, time
                deadline_time = datetime.strptime(race_deadline, '%H:%M').time()
                race_closed_at = datetime.combine(race_date, deadline_time).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
        
        # Parse subtitle and distance
        race_subtitle, race_distance = self._parse_subtitle_distance(race_subtitle_distance)
        
        return {
            'race_date': race_date.strftime('%Y-%m-%d'),
            'race_stadium_number': race_stadium_number,
            'race_number': race_number,
            'race_closed_at': race_closed_at,
            'race_grade_number': race_grade_number,
            'race_title': race_title,
            'race_subtitle': race_subtitle,
            'race_distance': race_distance,
        }
    
    def _scrape_boats(self, soup) -> Dict[str, Any]:
        """Extract boat and racer information."""
        boats = {}
        
        # CSS selector templates for boat/racer data
        base_selector = f'body main div div div div:nth-child(2) div:nth-child({self.base_level + 5}) table'
        
        for boat_number in range(1, 7):  # Boats 1-6
            tbody_selector = f'{base_selector} tbody:nth-child({boat_number})'
            
            # Extract boat data
            boat_data = self._extract_boat_data(soup, tbody_selector, boat_number)
            if boat_data:
                boats[boat_number] = boat_data
        
        return {'boats': boats}
    
    def _extract_boat_data(self, soup, tbody_selector: str, default_boat_number: int) -> Optional[Dict[str, Any]]:
        """Extract data for a single boat."""
        
        # CSS selectors for boat data
        selectors = {
            'boat_number': f'{tbody_selector} tr:nth-child(1) td:nth-child(1)',
            'racer_name': f'{tbody_selector} tr:nth-child(1) td:nth-child(3) div:nth-child(2) a',
            'racer_number_class': f'{tbody_selector} tr:nth-child(1) td:nth-child(3) div:nth-child(1)',
            'racer_branch_birthplace_age_weight': f'{tbody_selector} tr:nth-child(1) td:nth-child(3) div:nth-child(3)',
            'racer_flying_late_start_timing': f'{tbody_selector} tr:nth-child(1) td:nth-child(4)',
            'racer_national_top123_percent': f'{tbody_selector} tr:nth-child(1) td:nth-child(5)',
            'racer_local_top123_percent': f'{tbody_selector} tr:nth-child(1) td:nth-child(6)',
            'racer_assigned_motor_number_top23_percent': f'{tbody_selector} tr:nth-child(1) td:nth-child(7)',
            'racer_assigned_boat_number_top23_percent': f'{tbody_selector} tr:nth-child(1) td:nth-child(8)',
        }
        
        # Extract raw data
        raw_data = {}
        for key, selector in selectors.items():
            raw_data[key] = self.filter_xpath_text(soup, selector)
        
        # Parse boat number
        boat_number = self._parse_int(raw_data['boat_number']) or default_boat_number
        
        # Parse racer name
        racer_name = self._clean_racer_name(raw_data['racer_name'])
        
        # Parse number and class
        racer_number, racer_class_number = self._parse_number_class(raw_data['racer_number_class'])
        
        # Parse branch, birthplace, age, weight
        (racer_branch_number, racer_birthplace_number, 
         racer_age, racer_weight) = self._parse_branch_birthplace_age_weight(
            raw_data['racer_branch_birthplace_age_weight'])
        
        # Parse flying, late, start timing
        (racer_flying_count, racer_late_count,
         racer_average_start_timing) = self._parse_flying_late_start_timing(
            raw_data['racer_flying_late_start_timing'])
        
        # Parse national percentages
        (racer_national_top_1_percent, racer_national_top_2_percent,
         racer_national_top_3_percent) = self._parse_top123_percent(
            raw_data['racer_national_top123_percent'])
        
        # Parse local percentages
        (racer_local_top_1_percent, racer_local_top_2_percent,
         racer_local_top_3_percent) = self._parse_top123_percent(
            raw_data['racer_local_top123_percent'])
        
        # Parse motor data
        (racer_assigned_motor_number, racer_assigned_motor_top_2_percent,
         racer_assigned_motor_top_3_percent) = self._parse_assigned_motor_number_top23_percent(
            raw_data['racer_assigned_motor_number_top23_percent'])
        
        # Parse boat data
        (racer_assigned_boat_number, racer_assigned_boat_top_2_percent,
         racer_assigned_boat_top_3_percent) = self._parse_assigned_boat_number_top23_percent(
            raw_data['racer_assigned_boat_number_top23_percent'])
        
        return {
            'racer_boat_number': boat_number,
            'racer_name': racer_name,
            'racer_number': racer_number,
            'racer_class_number': racer_class_number,
            'racer_branch_number': racer_branch_number,
            'racer_birthplace_number': racer_birthplace_number,
            'racer_age': racer_age,
            'racer_weight': racer_weight,
            'racer_flying_count': racer_flying_count,
            'racer_late_count': racer_late_count,
            'racer_average_start_timing': racer_average_start_timing,
            'racer_national_top_1_percent': racer_national_top_1_percent,
            'racer_national_top_2_percent': racer_national_top_2_percent,
            'racer_national_top_3_percent': racer_national_top_3_percent,
            'racer_local_top_1_percent': racer_local_top_1_percent,
            'racer_local_top_2_percent': racer_local_top_2_percent,
            'racer_local_top_3_percent': racer_local_top_3_percent,
            'racer_assigned_motor_number': racer_assigned_motor_number,
            'racer_assigned_motor_top_2_percent': racer_assigned_motor_top_2_percent,
            'racer_assigned_motor_top_3_percent': racer_assigned_motor_top_3_percent,
            'racer_assigned_boat_number': racer_assigned_boat_number,
            'racer_assigned_boat_top_2_percent': racer_assigned_boat_top_2_percent,
            'racer_assigned_boat_top_3_percent': racer_assigned_boat_top_3_percent,
        }
    
    # Helper parsing methods
    def _parse_subtitle_distance(self, subtitle_distance: Optional[str]) -> tuple[Optional[str], Optional[int]]:
        """Parse race subtitle and distance."""
        if not subtitle_distance:
            return None, None
        
        # Look for distance pattern (number + 'm')
        distance_match = re.search(r'(\d+)m', subtitle_distance)
        distance = int(distance_match.group(1)) if distance_match else None
        
        # Subtitle is everything except the distance part
        subtitle = re.sub(r'\s*\d+m\s*', '', subtitle_distance).strip()
        subtitle = subtitle if subtitle else None
        
        return subtitle, distance
    
    def _parse_int(self, value: Optional[str]) -> Optional[int]:
        """Parse integer value safely."""
        if not value:
            return None
        try:
            return int(re.sub(r'[^\d]', '', value))
        except (ValueError, TypeError):
            return None
    
    def _parse_float(self, value: Optional[str]) -> Optional[float]:
        """Parse float value safely."""
        if not value:
            return None
        try:
            return float(re.sub(r'[^\d.]', '', value))
        except (ValueError, TypeError):
            return None
    
    def _clean_racer_name(self, name: Optional[str]) -> Optional[str]:
        """Clean racer name."""
        return name.strip() if name else None
    
    def _parse_number_class(self, text: Optional[str]) -> tuple[Optional[int], Optional[str]]:
        """Parse racer number and class."""
        if not text:
            return None, None
        
        # Extract number (usually at start)
        number_match = re.search(r'(\d+)', text)
        number = int(number_match.group(1)) if number_match else None
        
        # Extract class (A1, A2, B1, B2)
        class_match = re.search(r'([AB][12])', text)
        class_str = class_match.group(1) if class_match else None
        
        return number, class_str
    
    def _parse_branch_birthplace_age_weight(self, text: Optional[str]) -> tuple[Optional[int], Optional[int], Optional[int], Optional[float]]:
        """Parse branch, birthplace, age, and weight."""
        if not text:
            return None, None, None, None
        
        # This would need specific logic based on the actual format
        # For now, return None values as placeholders
        return None, None, None, None
    
    def _parse_flying_late_start_timing(self, text: Optional[str]) -> tuple[Optional[int], Optional[int], Optional[float]]:
        """Parse flying count, late count, and average start timing."""
        if not text:
            return None, None, None
        
        # This would need specific logic based on the actual format
        return None, None, None
    
    def _parse_top123_percent(self, text: Optional[str]) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """Parse top 1, 2, 3 percentages."""
        if not text:
            return None, None, None
        
        # Look for percentage patterns
        percentages = re.findall(r'(\d+(?:\.\d+)?)%?', text)
        percentages = [float(p) for p in percentages[:3]]  # Take first 3
        
        # Pad with None if not enough values
        while len(percentages) < 3:
            percentages.append(None)
        
        return tuple(percentages[:3])
    
    def _parse_assigned_motor_number_top23_percent(self, text: Optional[str]) -> tuple[Optional[int], Optional[float], Optional[float]]:
        """Parse motor number and top 2, 3 percentages."""
        if not text:
            return None, None, None
        
        # Extract motor number (usually first number)
        number_match = re.search(r'(\d+)', text)
        motor_number = int(number_match.group(1)) if number_match else None
        
        # Extract percentages
        percentages = re.findall(r'(\d+(?:\.\d+)?)%?', text)
        percentages = [float(p) for p in percentages[1:3]]  # Skip first (motor number)
        
        top_2_percent = percentages[0] if len(percentages) > 0 else None
        top_3_percent = percentages[1] if len(percentages) > 1 else None
        
        return motor_number, top_2_percent, top_3_percent
    
    def _parse_assigned_boat_number_top23_percent(self, text: Optional[str]) -> tuple[Optional[int], Optional[float], Optional[float]]:
        """Parse boat number and top 2, 3 percentages."""
        if not text:
            return None, None, None
        
        # Similar to motor parsing
        number_match = re.search(r'(\d+)', text)
        boat_number = int(number_match.group(1)) if number_match else None
        
        percentages = re.findall(r'(\d+(?:\.\d+)?)%?', text)
        percentages = [float(p) for p in percentages[1:3]]  # Skip first (boat number)
        
        top_2_percent = percentages[0] if len(percentages) > 0 else None
        top_3_percent = percentages[1] if len(percentages) > 1 else None
        
        return boat_number, top_2_percent, top_3_percent