import time
import threading
from typing import Dict, Any
from app.utils.advanced_cv_parser import AdvancedCVParser
from app.utils.cv_parser import CVParser

class HybridParser:
    """Hybrid CV parser - Quick parse first, deep parse in background"""
    
    def __init__(self):
        self.quick_parser = AdvancedCVParser()
        self.deep_parser = AdvancedCVParser()
        self.cache = {}
    
    def parse_hybrid(self, file_path: str, user_id: int) -> Dict[str, Any]:
        """
        Hybrid parsing: Quick parse (3s) then deep parse in background
        """
        # Check cache first
        cache_key = f"{user_id}_{file_path}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Step 1: Extract text
        text = self._extract_text(file_path)
        if not text:
            return None
        
        # Step 2: Quick parse (fast, less accurate)
        quick_results = self._quick_parse(text)
        
        # Step 3: Start deep parse in background thread
        self._start_deep_parse(text, quick_results, cache_key, user_id)
        
        # Step 4: Return quick results immediately
        quick_results['status'] = 'processing'
        quick_results['deep_parse_started'] = True
        
        # Store in cache
        self.cache[cache_key] = quick_results
        
        return quick_results
    
    def _quick_parse(self, text: str) -> Dict[str, Any]:
        """Quick parse - fast but less accurate (2-3 seconds)"""
        start_time = time.time()
        
        # Use quick parsing method
        results = self.quick_parser.parse_cv_quick(text)
        
        # Add timing info
        results['parse_time'] = round(time.time() - start_time, 2)
        results['parse_type'] = 'quick'
        
        return results
    
    def _deep_parse(self, text: str, quick_results: Dict, cache_key: str) -> Dict:
        """Deep parse - slow but accurate (5-10 seconds)"""
        start_time = time.time()
        
        # Use full parsing
        deep_results = self.deep_parser.parse_cv(text)
        
        # Merge results
        merged = {**quick_results, **deep_results}
        merged['parse_time'] = round(time.time() - start_time, 2)
        merged['parse_type'] = 'deep'
        merged['status'] = 'complete'
        
        # Update cache
        self.cache[cache_key] = merged
        
        return merged
    
    def _start_deep_parse(self, text: str, quick_results: Dict, cache_key: str, user_id: int):
        """Start deep parse in background thread"""
        def parse_in_background():
            try:
                self._deep_parse(text, quick_results, cache_key)
                print(f"✅ Deep parse complete for user {user_id}")
            except Exception as e:
                print(f"❌ Deep parse error: {e}")
        
        thread = threading.Thread(target=parse_in_background)
        thread.daemon = True
        thread.start()
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from file"""
        import os
        from PyPDF2 import PdfReader
        from docx import Document
        
        text = ""
        
        if file_path.endswith('.pdf'):
            try:
                reader = PdfReader(file_path)
                max_pages = min(len(reader.pages), 5)
                for i in range(max_pages):
                    text += reader.pages[i].extract_text()
            except Exception as e:
                print(f"PDF error: {e}")
                
        elif file_path.endswith('.docx'):
            try:
                doc = Document(file_path)
                max_paras = min(len(doc.paragraphs), 50)
                for i in range(max_paras):
                    text += doc.paragraphs[i].text + "\n"
            except Exception as e:
                print(f"DOCX error: {e}")
        
        return text
    
    def get_parsed_data(self, user_id: int, file_path: str) -> Dict:
        """Get parsed data from cache or return None"""
        cache_key = f"{user_id}_{file_path}"
        return self.cache.get(cache_key)
    
    def is_parsing_complete(self, user_id: int, file_path: str) -> bool:
        """Check if deep parsing is complete"""
        cache_key = f"{user_id}_{file_path}"
        data = self.cache.get(cache_key)
        if data:
            return data.get('status') == 'complete'
        return False