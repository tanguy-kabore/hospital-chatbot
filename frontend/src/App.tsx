import React, { useState, ChangeEvent, KeyboardEvent, useRef, useEffect } from 'react';
import {
  Box,
  Input,
  Button,
  Text,
  VStack,
  Container,
  Flex,
  Icon,
  InputGroup,
  InputRightElement,
  useColorModeValue,
  Avatar,
  List,
  ListItem,
  ListIcon,
} from '@chakra-ui/react';
import { FaRobot, FaPaperPlane, FaUser, FaStar } from 'react-icons/fa';

interface Message {
  text: string;
  isUser: boolean;
  items?: string[];
}

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const exampleQuestions = [
    "Quels sont les hôpitaux disponibles?",
    "Quels médecins sont disponibles?",
    "Pouvez-vous me donner des informations sur les patients?",
    "Quels sont les avis des patients sur l'hôpital Wheeler?",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const chatBgColor = useColorModeValue('white', 'gray.800');
  const userMessageBg = 'teal.500';
  const botMessageBg = useColorModeValue('gray.100', 'gray.700');
  const inputBgColor = useColorModeValue('white', 'gray.800');

  const formatMessage = (text: string): Message => {
    const lines = text.split('\n');
    const items: string[] = [];
    let mainText = '';

    lines.forEach(line => {
      if (line.includes('*')) {
        items.push(line.replace('*', '').trim());
      } else {
        mainText += line + ' ';
      }
    });

    return {
      text: mainText.trim(),
      isUser: false,
      items: items.length > 0 ? items : undefined
    };
  };

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Server error: ${errorData}`);
      }

      const data = await response.json();
      setMessages(prev => [...prev, formatMessage(data.response)]);
    } catch (error) {
      console.error('Failed to get response:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const renderMessageContent = (message: Message) => {
    if (message.isUser) {
      return <Text>{message.text}</Text>;
    }

    return (
      <Box>
        {message.text && <Text mb={message.items ? 3 : 0}>{message.text}</Text>}
        {message.items && (
          <List spacing={2}>
            {message.items.map((item, index) => (
              <ListItem 
                key={index}
                display="flex"
                alignItems="center"
                fontWeight="500"
              >
                <ListIcon as={FaStar} color="yellow.400" />
                {item}
              </ListItem>
            ))}
          </List>
        )}
      </Box>
    );
  };

  return (
    <Box bg={bgColor} minH="100vh" py={8}>
      <Container maxW="container.md" h="calc(100vh - 64px)">
        <Box
          bg={chatBgColor}
          borderRadius="lg"
          boxShadow="lg"
          overflow="hidden"
          h="100%"
          display="flex"
          flexDirection="column"
        >
          <Flex
            bg="teal.500"
            color="white"
            p={4}
            alignItems="center"
            borderBottom="1px"
            borderColor="teal.600"
          >
            <Icon as={FaRobot} w={6} h={6} mr={3} />
            <Text fontSize="lg" fontWeight="bold">Assistant Hospitalier</Text>
          </Flex>

          <VStack
            flex={1}
            overflowY="auto"
            spacing={4}
            p={4}
            css={{
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                background: 'transparent',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#CBD5E0',
                borderRadius: '4px',
              },
            }}
          >
            {messages.map((message, idx) => (
              <Flex
                key={idx}
                w="100%"
                justify={message.isUser ? 'flex-end' : 'flex-start'}
              >
                <Flex
                  maxW="80%"
                  alignItems="flex-start"
                  gap={2}
                  order={message.isUser ? 1 : 0}
                >
                  {!message.isUser && (
                    <Avatar
                      size="sm"
                      icon={<Icon as={FaRobot} />}
                      bg="teal.500"
                      color="white"
                    />
                  )}
                  <Box
                    bg={message.isUser ? userMessageBg : botMessageBg}
                    color={message.isUser ? 'white' : 'black'}
                    px={4}
                    py={3}
                    borderRadius="lg"
                    boxShadow="sm"
                  >
                    {renderMessageContent(message)}
                  </Box>
                  {message.isUser && (
                    <Avatar
                      size="sm"
                      icon={<Icon as={FaUser} />}
                      bg="teal.500"
                      color="white"
                    />
                  )}
                </Flex>
              </Flex>
            ))}
            <div ref={messagesEndRef} />
          </VStack>

          {messages.length === 0 && (
            <Box p={4} borderTop="1px" borderColor="gray.200">
              <Text mb={2} color="gray.600">Exemples de questions :</Text>
              <List spacing={2}>
                {exampleQuestions.map((question, index) => (
                  <ListItem 
                    key={index}
                    cursor="pointer"
                    color="teal.600"
                    _hover={{ color: 'teal.500' }}
                    onClick={() => {
                      setInput(question);
                      handleSubmit();
                    }}
                  >
                    <ListIcon as={FaStar} color="yellow.400" />
                    {question}
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          <Box p={4} bg={chatBgColor} borderTop="1px" borderColor="gray.200">
            <InputGroup size="lg">
              <Input
                value={input}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder="Posez votre question..."
                bg={inputBgColor}
                borderRadius="full"
                pr="4.5rem"
                _focus={{
                  borderColor: 'teal.500',
                  boxShadow: '0 0 0 1px teal.500',
                }}
              />
              <InputRightElement width="4.5rem">
                <Button
                  h="1.75rem"
                  size="sm"
                  colorScheme="teal"
                  isLoading={loading}
                  onClick={handleSubmit}
                  borderRadius="full"
                  _hover={{ bg: 'teal.600' }}
                >
                  <Icon as={FaPaperPlane} />
                </Button>
              </InputRightElement>
            </InputGroup>
          </Box>
        </Box>
      </Container>
    </Box>
  );
}

export default App;
