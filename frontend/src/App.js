import { useState, useEffect, useRef } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Loader2, Send, BookOpen, Brain, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AmbedkarGPT = () => {
  const [question, setQuestion] = useState('');
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    checkStatus();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [conversations]);

  const checkStatus = async () => {
    try {
      const response = await axios.get(`${API}/ambedkar/status`);
      setInitialized(response.data.initialized);
      if (!response.data.initialized) {
        initializeRAG();
      }
    } catch (error) {
      console.error('Error checking status:', error);
    }
  };

  const initializeRAG = async () => {
    setInitializing(true);
    try {
      const response = await axios.post(`${API}/ambedkar/init`);
      setInitialized(true);
      toast.success('AmbedkarGPT initialized successfully!');
    } catch (error) {
      console.error('Error initializing:', error);
      toast.error('Failed to initialize. Please refresh the page.');
    } finally {
      setInitializing(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) {
      toast.error('Please enter a question');
      return;
    }

    const userQuestion = question.trim();
    setQuestion('');
    setLoading(true);

    // Add user question to conversation
    setConversations(prev => [...prev, { type: 'question', content: userQuestion }]);

    try {
      const response = await axios.post(`${API}/ambedkar/ask`, {
        question: userQuestion
      });

      // Add answer to conversation
      setConversations(prev => [
        ...prev,
        {
          type: 'answer',
          content: response.data.answer,
          sources: response.data.sources,
          sources_count: response.data.sources_count
        }
      ]);
    } catch (error) {
      console.error('Error asking question:', error);
      toast.error('Failed to get answer. Please try again.');
      setConversations(prev => [
        ...prev,
        { type: 'error', content: 'Failed to get answer. Please try again.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  const sampleQuestions = [
    'What is the real remedy according to Dr. Ambedkar?',
    'What does Dr. Ambedkar say about the shastras?',
    'How does Dr. Ambedkar compare social reform to gardening?',
    'What is the real enemy according to this speech?'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-amber-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-amber-600 to-orange-600 rounded-xl flex items-center justify-center shadow-lg">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-amber-900">AmbedkarGPT</h1>
              <p className="text-sm text-amber-700">Annihilation of Caste Q&A</p>
            </div>
          </div>
          <Badge variant="secondary" className="bg-amber-100 text-amber-800 border-amber-300">
            {initialized ? (
              <><Sparkles className="w-3 h-3 mr-1" /> Ready</>
            ) : (
              <><Loader2 className="w-3 h-3 mr-1 animate-spin" /> Initializing...</>
            )}
          </Badge>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Welcome Card */}
        {conversations.length === 0 && (
          <Card className="mb-6 border-amber-200 bg-white/80 backdrop-blur-sm shadow-xl" data-testid="welcome-card">
            <CardHeader>
              <CardTitle className="text-2xl text-amber-900 flex items-center gap-2">
                <Brain className="w-6 h-6" />
                Welcome to AmbedkarGPT
              </CardTitle>
              <CardDescription className="text-base text-amber-700">
                Ask questions about Dr. B.R. Ambedkar's powerful speech on caste and social reform.
                This AI-powered system uses RAG (Retrieval-Augmented Generation) to provide accurate answers based on the speech text.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-sm font-semibold text-amber-800">Try these sample questions:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {sampleQuestions.map((q, idx) => (
                    <Button
                      key={idx}
                      variant="outline"
                      className="justify-start text-left h-auto py-3 px-4 border-amber-300 hover:bg-amber-50 hover:border-amber-400 transition-all"
                      onClick={() => setQuestion(q)}
                      data-testid={`sample-question-${idx}`}
                    >
                      <span className="text-sm text-amber-900">{q}</span>
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Conversation Area */}
        {conversations.length > 0 && (
          <Card className="mb-6 border-amber-200 bg-white/80 backdrop-blur-sm shadow-xl" data-testid="conversation-card">
            <ScrollArea className="h-[500px] p-6" ref={scrollRef}>
              <div className="space-y-6">
                {conversations.map((conv, idx) => (
                  <div key={idx} className={conv.type === 'question' ? 'flex justify-end' : 'flex justify-start'}>
                    {conv.type === 'question' && (
                      <div className="max-w-[80%] bg-gradient-to-br from-amber-600 to-orange-600 text-white rounded-2xl rounded-tr-sm px-5 py-3 shadow-md" data-testid={`question-${idx}`}>
                        <p className="text-sm font-medium">{conv.content}</p>
                      </div>
                    )}
                    {conv.type === 'answer' && (
                      <div className="max-w-[85%] space-y-3" data-testid={`answer-${idx}`}>
                        <div className="bg-white border border-amber-200 rounded-2xl rounded-tl-sm px-5 py-4 shadow-md">
                          <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">{conv.content}</p>
                        </div>
                        {conv.sources && conv.sources.length > 0 && (
                          <div className="pl-4">
                            <p className="text-xs text-amber-700 font-semibold mb-2">📚 Retrieved {conv.sources_count} source(s)</p>
                          </div>
                        )}
                      </div>
                    )}
                    {conv.type === 'error' && (
                      <div className="max-w-[80%] bg-red-100 border border-red-300 text-red-800 rounded-2xl rounded-tl-sm px-5 py-3 shadow-md" data-testid={`error-${idx}`}>
                        <p className="text-sm">{conv.content}</p>
                      </div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start" data-testid="loading-indicator">
                    <div className="bg-white border border-amber-200 rounded-2xl rounded-tl-sm px-5 py-4 shadow-md">
                      <div className="flex items-center gap-2 text-amber-700">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>
          </Card>
        )}

        {/* Input Area */}
        <Card className="border-amber-200 bg-white/80 backdrop-blur-sm shadow-xl" data-testid="input-card">
          <CardContent className="pt-6">
            <div className="flex gap-3">
              <Textarea
                placeholder="Ask your question about Dr. Ambedkar's speech..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyPress={handleKeyPress}
                className="min-h-[80px] resize-none border-amber-300 focus:border-amber-500 focus:ring-amber-500"
                disabled={!initialized || loading}
                data-testid="question-input"
              />
              <Button
                onClick={handleAsk}
                disabled={!initialized || loading || !question.trim()}
                className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white shadow-lg h-[80px] px-8"
                data-testid="ask-button"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Info Footer */}
        <div className="mt-6 text-center text-sm text-amber-700">
          <p>Powered by Ollama (Mistral 7B) • LangChain • ChromaDB • HuggingFace Embeddings</p>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AmbedkarGPT />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
