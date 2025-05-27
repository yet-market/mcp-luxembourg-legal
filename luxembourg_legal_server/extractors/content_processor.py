"""
Content processor for Luxembourg legal documents.

Orchestrates HTML/PDF extraction and provides unified content processing.
"""

import logging
from typing import Optional, Dict, Any, List
from luxembourg_legal_server.extractors.html_extractor import HTMLExtractor
from luxembourg_legal_server.extractors.pdf_extractor import PDFExtractor

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Processes and enriches Luxembourg legal document content."""
    
    def __init__(self, pdf_timeout: int = 60):
        """Initialize the content processor.
        
        Args:
            pdf_timeout: Timeout for PDF requests
        """
        self.html_extractor = HTMLExtractor()
        self.pdf_extractor = PDFExtractor(timeout=pdf_timeout)
    
    def extract_entity_content(self, entity_uri: str, prefer_html: bool = True) -> Optional[Dict[str, Any]]:
        """Extract content from a Luxembourg entity URI.
        
        Args:
            entity_uri: The base URI of the Luxembourg entity
            prefer_html: Whether to try HTML first (faster) or PDF first
            
        Returns:
            Dictionary with extracted content and metadata
        """
        if prefer_html:
            # Try HTML first (faster parsing)
            content = self.html_extractor.extract_content(entity_uri)
            if content and content.get('text'):
                logger.info(f"Successfully extracted HTML content for: {entity_uri}")
                return self._enrich_content(content, entity_uri)
            
            # Fallback to PDF if HTML fails
            logger.info(f"HTML extraction failed, trying PDF for: {entity_uri}")
            content = self.pdf_extractor.extract_content(entity_uri)
            if content and content.get('text'):
                logger.info(f"Successfully extracted PDF content for: {entity_uri}")
                return self._enrich_content(content, entity_uri)
        else:
            # Try PDF first
            content = self.pdf_extractor.extract_content(entity_uri)
            if content and content.get('text'):
                logger.info(f"Successfully extracted PDF content for: {entity_uri}")
                return self._enrich_content(content, entity_uri)
            
            # Fallback to HTML
            logger.info(f"PDF extraction failed, trying HTML for: {entity_uri}")
            content = self.html_extractor.extract_content(entity_uri)
            if content and content.get('text'):
                logger.info(f"Successfully extracted HTML content for: {entity_uri}")
                return self._enrich_content(content, entity_uri)
        
        logger.warning(f"Failed to extract content from both HTML and PDF for: {entity_uri}")
        return None
    
    def _enrich_content(self, content: Dict[str, Any], entity_uri: str) -> Dict[str, Any]:
        """Enrich extracted content with additional metadata and processing.
        
        Args:
            content: Extracted content dictionary
            entity_uri: Original entity URI
            
        Returns:
            Enriched content dictionary
        """
        # Add entity URI to metadata
        content['entity_uri'] = entity_uri
        
        # Analyze document structure
        structure_info = self._analyze_document_structure(content['text'])
        content['structure'] = structure_info
        
        # Detect document type
        doc_type = self._detect_document_type(content['text'], content.get('title', ''))
        content['document_type'] = doc_type
        
        # Extract key legal concepts
        legal_concepts = self._extract_legal_concepts(content['text'])
        content['legal_concepts'] = legal_concepts
        
        # Generate summary for AI context
        summary = self._generate_summary(content['text'], content.get('title', ''))
        content['summary'] = summary
        
        return content
    
    def _analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """Analyze the structure of a legal document.
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with structure information
        """
        lines = text.split('\n')
        structure = {
            'total_lines': len(lines),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'has_articles': False,
            'has_chapters': False,
            'has_sections': False,
            'estimated_reading_time_minutes': max(1, len(text.split()) // 200)  # ~200 words per minute
        }
        
        text_lower = text.lower()
        
        # Detect common legal document structures
        if any(marker in text_lower for marker in ['article', 'art.', 'art ']):
            structure['has_articles'] = True
        
        if any(marker in text_lower for marker in ['chapitre', 'chapter']):
            structure['has_chapters'] = True
        
        if any(marker in text_lower for marker in ['section', 'titre', 'title']):
            structure['has_sections'] = True
        
        return structure
    
    def _detect_document_type(self, text: str, title: str) -> str:
        """Detect the type of legal document.
        
        Args:
            text: Document text
            title: Document title
            
        Returns:
            Detected document type
        """
        combined_text = (title + ' ' + text[:1000]).lower()
        
        # Legal document type patterns (Luxembourg specific)
        type_patterns = {
            'loi': ['loi', 'law'],
            'règlement': ['règlement', 'regulation', 'reglement'],
            'arrêté': ['arrêté', 'arrete', 'ministerial'],
            'décret': ['décret', 'decree'],
            'code': ['code'],
            'constitution': ['constitution'],
            'circulaire': ['circulaire', 'circular'],
            'directive': ['directive'],
            'ordonnance': ['ordonnance'],
            'convention': ['convention', 'accord', 'agreement'],
            'jurisprudence': ['cour', 'tribunal', 'jugement', 'arrêt', 'court'],
            'company_info': ['société', 'company', 'enterprise', 'sàrl', 'sa ', 'rcs']
        }
        
        for doc_type, patterns in type_patterns.items():
            if any(pattern in combined_text for pattern in patterns):
                return doc_type
        
        return 'unknown'
    
    def _extract_legal_concepts(self, text: str) -> List[str]:
        """Extract key legal concepts from document text.
        
        Args:
            text: Document text
            
        Returns:
            List of detected legal concepts
        """
        text_lower = text.lower()
        concepts = []
        
        # Luxembourg legal concept patterns
        concept_patterns = {
            'tax': ['taxe', 'impôt', 'fiscal', 'tva', 'tax'],
            'employment': ['travail', 'emploi', 'salarié', 'employment', 'worker'],
            'corporate': ['société', 'entreprise', 'commercial', 'company', 'business'],
            'civil': ['civil', 'citoyen', 'citizen', 'droits civils'],
            'criminal': ['pénal', 'criminel', 'criminal', 'penal'],
            'administrative': ['administratif', 'administration', 'administrative'],
            'environmental': ['environnement', 'environmental', 'écologie'],
            'financial': ['financier', 'banque', 'finance', 'banking'],
            'insurance': ['assurance', 'insurance'],
            'property': ['propriété', 'immobilier', 'property', 'real estate']
        }
        
        for concept, patterns in concept_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                concepts.append(concept)
        
        return concepts
    
    def _generate_summary(self, text: str, title: str) -> str:
        """Generate a brief summary for AI context.
        
        Args:
            text: Document text
            title: Document title
            
        Returns:
            Brief summary of the document
        """
        # Take first few sentences as summary
        sentences = text.replace('\n', ' ').split('.')
        summary_sentences = []
        char_count = 0
        
        for sentence in sentences[:5]:  # Max 5 sentences
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                summary_sentences.append(sentence)
                char_count += len(sentence)
                if char_count > 300:  # Max ~300 chars
                    break
        
        summary = '. '.join(summary_sentences)
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return summary or title[:200]