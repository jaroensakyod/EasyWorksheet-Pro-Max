# ai_providers.py - AI Provider integrations (Google, Groq, OpenRouter)
from google import genai

class GoogleProvider:
    def __init__(self, api_key):
        self.api_key = api_key
        self.model = None
        self.model_name = None
        self.is_working = False
        self._init_model()
    
    def _init_model(self):
        try:
            client = genai.Client(api_key=self.api_key)
            model_priority = [
                'gemini-1.5-flash',
                'gemini-1.5-pro',
                'gemini-2.0-flash-exp',
            ]
            
            available_models = [m.name for m in client.models.list() if 'generateContent' in m.supported_generation_methods]
            
            for model_name in model_priority:
                for available in available_models:
                    if model_name in available:
                        self.model = available
                        self.model_name = available
                        self.is_working = True
                        return
            
            for m in available_models:
                if 'flash' in m.lower():
                    self.model = m
                    self.model_name = m
                    self.is_working = True
                    return
            
            if available_models:
                self.model = available_models[0]
                self.model_name = available_models[0]
                self.is_working = True
        except Exception as e:
            print(f"[!] Google API init failed: {e}")
            self.is_working = False
            self.model = None
    
    def test_connection(self):
        """Test if API is working"""
        return self.is_working
    
    def generate(self, prompt):
        if self.model and self.is_working:
            try:
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(model=self.model, contents=prompt)
                return response.text
            except Exception as e:
                print(f"[!] Google API error: {e}")
                self.is_working = False
                return None
        return None


class GroqProvider:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = None
        self.model_name = "llama-3.3-70b-versatile"
        self.is_working = False
        self._init_client()
    
    def _init_client(self):
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            # Test connection
            self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model=self.model_name,
                max_tokens=5
            )
            self.is_working = True
        except ImportError:
            print("[!] Groq library not installed")
            self.is_working = False
        except Exception as e:
            print(f"[!] Groq init failed: {e}")
            self.is_working = False
    
    def test_connection(self):
        """Test if API is working"""
        return self.is_working
    
    def generate(self, prompt):
        if self.client and self.is_working:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful Thai education assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    model=self.model_name,
                    temperature=0.7,
                )
                return chat_completion.choices[0].message.content
            except Exception as e:
                print(f"[!] Groq API error: {e}")
                self.is_working = False
                return None
        return None


class OpenRouterProvider:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = None
        self.model_name = "openrouter/auto"
        self.is_working = False
        self._init_client()
    
    def _init_client(self):
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            # Test connection
            self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model="openrouter/auto",
                max_tokens=5
            )
            self.is_working = True
        except ImportError:
            print("[!] OpenRouter library not installed")
            self.is_working = False
        except Exception as e:
            print(f"[!] OpenRouter init failed: {e}")
            self.is_working = False
    
    def test_connection(self):
        """Test if API is working"""
        return self.is_working
    
    def generate(self, prompt):
        if self.client and self.is_working:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful Thai education assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    model=self.model_name,
                    temperature=0.7,
                )
                return chat_completion.choices[0].message.content
            except Exception as e:
                print(f"[!] OpenRouter API error: {e}")
                self.is_working = False
                return None
        return None


def create_ai_provider(provider_name, api_key):
    """Factory function to create AI provider"""
    providers = {
        "Google Gemini": lambda: GoogleProvider(api_key),
        "Groq": lambda: GroqProvider(api_key),
        "OpenRouter": lambda: OpenRouterProvider(api_key),
    }
    
    if provider_name in providers:
        try:
            return providers[provider_name]()
        except Exception as e:
            print(f"[!] Failed to create {provider_name}: {e}")
            return None
    return None
