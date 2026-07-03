import time
import threading
from typing import Dict, Any
from app.utils.advanced_cv_parser import AdvancedCVParser

class HybridParser:
    """Hybrid CV parser - Quick parse first, deep parse in background"""
    
    def __init__(self):
        # Lazy load - only load when needed
        self._quick_parser = None
        self._deep_parser = None
        self.cache = {}
        self.processing_queue = {}
    
    def _get_quick_parser(self):
        """Lazy load quick parser"""
        if self._quick_parser is None:
            print("⏳ Loading quick parser...")
            self._quick_parser = AdvancedCVParser()
            print("✅ Quick parser loaded")
        return self._quick_parser
    
    def _get_deep_parser(self):
        """Lazy load deep parser"""
        if self._deep_parser is None:
            print("⏳ Loading deep parser...")
            self._deep_parser = AdvancedCVParser()
            print("✅ Deep parser loaded")
        return self._deep_parser
    
    def parse_hybrid(self, file_path: str, user_id: int) -> Dict[str, Any]:
        """Hybrid parsing: Quick parse first, deep parse in background"""
        
        print(f"🔍 HybridParser.parse_hybrid called for {file_path}")
        
        # Check cache first
        cache_key = f"{user_id}_{file_path}"
        if cache_key in self.cache:
            print(f"📦 Returning cached data for {cache_key}")
            return self.cache[cache_key]
        
        # Step 1: Extract text (optimized)
        print("📄 Extracting text...")
        text = self._extract_text_fast(file_path)
        if not text:
            print("❌ No text extracted")
            return None
        
        print(f"📄 Extracted {len(text)} characters, {len(text.split())} words")
        
        # Step 2: Quick parse
        print("⚡ Running quick parse...")
        quick_results = self._quick_parse(text)
        print(f"✅ Quick parse complete: {quick_results.get('total_skills', 0)} skills found")
        
        # If CV is small (under 500 words), skip deep parse
        word_count = len(text.split())
        if word_count < 500:
            print(f"📄 Small CV ({word_count} words) - skipping deep parse")
            quick_results['status'] = 'complete'
            quick_results['deep_parse_started'] = False
            quick_results['parse_type'] = 'quick_only'
            self.cache[cache_key] = quick_results
            return quick_results
        
        # Step 3: Start deep parse in background thread for larger CVs
        self._start_deep_parse(text, quick_results, cache_key, user_id)
        
        # Step 4: Return quick results immediately
        quick_results['status'] = 'processing'
        quick_results['deep_parse_started'] = True
        self.cache[cache_key] = quick_results
        
        print("✅ Returning quick results")
        return quick_results
    
    def _quick_parse(self, text: str) -> Dict[str, Any]:
        """Quick parse - fast but less accurate (1-2 seconds)"""
        start_time = time.time()
        
        # Use quick parsing method
        parser = self._get_quick_parser()
        results = parser.parse_cv_quick(text)
        
        # Ensure the results have the expected structure
        if 'skills' not in results:
            results['skills'] = {}
        
        # Add timing info
        results['parse_time'] = round(time.time() - start_time, 2)
        results['parse_type'] = 'quick'
        results['status'] = 'processing'
        
        print(f"⚡ Quick parse completed in {results['parse_time']}s")
        print(f"📊 Found {results['total_skills']} skills")
        print(f"📂 Skills: {results['skills'].keys()}")
        
        return results
    
    def _deep_parse(self, text: str, quick_results: Dict, cache_key: str) -> Dict:
        """Deep parse - slow but accurate (runs in background)"""
        start_time = time.time()
        
        try:
            print(f"🔍 Starting deep parse for {cache_key}...")
            
            # Use full parsing
            parser = self._get_deep_parser()
            deep_results = parser.parse_cv(text)
            
            # Merge results
            merged = {**quick_results, **deep_results}
            merged['parse_time'] = round(time.time() - start_time, 2)
            merged['parse_type'] = 'deep'
            merged['status'] = 'complete'
            
            # Update cache
            self.cache[cache_key] = merged
            self.processing_queue.pop(cache_key, None)
            
            print(f"✅ Deep parse complete for {cache_key} in {merged['parse_time']}s")
            print(f"📊 Total skills: {merged['total_skills']}")
            return merged
            
        except Exception as e:
            print(f"❌ Deep parse error for {cache_key}: {e}")
            self.processing_queue.pop(cache_key, None)
            # Return quick results as fallback
            quick_results['status'] = 'complete'
            quick_results['deep_parse_started'] = False
            quick_results['parse_error'] = str(e)
            return quick_results
    
    def _start_deep_parse(self, text: str, quick_results: Dict, cache_key: str, user_id: int):
        """Start deep parse in background thread"""
        
        # Prevent duplicate processing
        if cache_key in self.processing_queue:
            print(f"⏳ {cache_key} already processing")
            return
        
        self.processing_queue[cache_key] = True
        
        def parse_in_background():
            try:
                # Wait a bit before starting deep parse (let user see quick results first)
                time.sleep(2)
                self._deep_parse(text, quick_results, cache_key)
            except Exception as e:
                print(f"❌ Background parse error: {e}")
                self.processing_queue.pop(cache_key, None)
        
        thread = threading.Thread(target=parse_in_background)
        thread.daemon = True
        thread.start()
        print(f"🔄 Background deep parse started for {cache_key}")
    
    def _extract_text_fast(self, file_path: str) -> str:
        """Extract text from file - optimized for speed"""
        import os
        from PyPDF2 import PdfReader
        from docx import Document
        
        text = ""
        
        if file_path.endswith('.pdf'):
            try:
                reader = PdfReader(file_path)
                # Only read first 3 pages for quick parse
                max_pages = min(len(reader.pages), 3)
                print(f"📄 Reading PDF: {max_pages} pages")
                for i in range(max_pages):
                    page_text = reader.pages[i].extract_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception as e:
                print(f"PDF error: {e}")
                
        elif file_path.endswith('.docx'):
            try:
                doc = Document(file_path)
                # Only read first 30 paragraphs
                max_paras = min(len(doc.paragraphs), 30)
                print(f"📄 Reading DOCX: {max_paras} paragraphs")
                for i in range(max_paras):
                    text += doc.paragraphs[i].text + "\n"
            except Exception as e:
                print(f"DOCX error: {e}")
        
        print(f"📄 Extracted {len(text)} characters")
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
    
    def get_parse_status(self, user_id: int, file_path: str) -> Dict:
        """Get detailed parse status"""
        cache_key = f"{user_id}_{file_path}"
        data = self.cache.get(cache_key)
        if data:
            return {
                'status': data.get('status', 'unknown'),
                'parse_type': data.get('parse_type', 'unknown'),
                'total_skills': data.get('total_skills', 0),
                'parse_time': data.get('parse_time', 0),
                'deep_parse_started': data.get('deep_parse_started', False)
            }
        return {'status': 'not_found'}
    
    def clear_cache(self, user_id: int = None):
        """Clear cache for a user or all users"""
        if user_id:
            keys_to_delete = [k for k in self.cache.keys() if k.startswith(f"{user_id}_")]
            for key in keys_to_delete:
                del self.cache[key]
            print(f"🧹 Cleared cache for user {user_id}")
        else:
            self.cache.clear()
            print("🧹 Cleared all cache")