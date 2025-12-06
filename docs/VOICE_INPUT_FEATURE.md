# Voice Input Feature Documentation

## Overview

The voice input feature allows users to report IT issues using speech instead of typing. This feature uses the Web Speech API (Speech Recognition) to convert spoken words into text, which is then sent to the AI chatbot.

## Features

- ✅ **Speech-to-Text Conversion** - Converts spoken words to text in real-time
- ✅ **Interim Results** - Shows what you're saying while speaking
- ✅ **Visual Feedback** - Visual indicators when listening
- ✅ **Error Handling** - Graceful error messages for unsupported browsers or permission issues
- ✅ **Auto-stop** - Automatically stops listening when speech ends

## Browser Support

The voice input feature uses the **Web Speech API**, which is supported in:

- ✅ Chrome/Edge (Chromium) - Full support
- ✅ Safari (iOS 14.5+) - Full support
- ✅ Firefox - Not supported (will show fallback message)
- ⚠️ Older browsers - Not supported

**Note:** The feature requires microphone permissions. Users will be prompted to allow microphone access when they first use the feature.

## How to Use

1. **Start Voice Input**
   - Click the microphone icon (🎤) button next to the text input field
   - The button will turn red and show "Listening..." indicator
   - Grant microphone permission if prompted

2. **Speak Your Issue**
   - Clearly describe your IT problem
   - Example: "My laptop is running very slow"
   - The system will show interim results as you speak

3. **Stop Listening**
   - The system automatically stops when you finish speaking
   - Or click the microphone button again to stop manually
   - Your transcribed text will appear in the input field

4. **Send Message**
   - Review the transcribed text
   - Edit if needed
   - Click "Send" or press Enter to submit

## Visual Indicators

### Listening State
- **Red pulsing button** - Indicates active listening
- **"Listening..." banner** - Shows at the top of input area
- **Interim transcript** - Shows what you're saying in real-time

### Error States
- **Permission denied** - "Microphone permission denied" message
- **No microphone** - "No microphone found" message
- **No speech detected** - "No speech detected" message

## Technical Implementation

### Architecture

```
ChatPage Component
    ↓
VoiceService (Singleton)
    ↓
Web Speech API (Browser)
    ↓
Speech Recognition
```

### Key Files

- `frontend/src/services/voiceService.js` - Voice service implementation
- `frontend/src/App.jsx` - ChatPage component with voice integration
- `frontend/src/styles/App.css` - Voice button and indicator styles

### Service Methods

```javascript
voiceService.startListening()  // Start voice recognition
voiceService.stopListening()    // Stop voice recognition
voiceService.checkSupport()     // Check browser support
voiceService.getListeningState() // Get current listening state
```

### Callbacks

- `onResult(result)` - Called when speech is recognized
- `onError(error)` - Called when an error occurs
- `onStart()` - Called when recognition starts
- `onEnd()` - Called when recognition ends

## Safety & Privacy

- ✅ **No audio storage** - Audio is processed in real-time, not stored
- ✅ **Client-side only** - All processing happens in the browser
- ✅ **User control** - Users can stop listening at any time
- ✅ **Permission-based** - Requires explicit user permission

## Troubleshooting

### Microphone Not Working

1. **Check browser permissions**
   - Chrome: Settings → Privacy → Site Settings → Microphone
   - Allow microphone access for the site

2. **Check microphone hardware**
   - Ensure microphone is connected and working
   - Test in other applications

3. **Browser compatibility**
   - Use Chrome/Edge for best support
   - Firefox doesn't support Web Speech API

### Voice Recognition Not Accurate

- Speak clearly and at a moderate pace
- Reduce background noise
- Use a good quality microphone
- Check internet connection (some browsers use cloud recognition)

### Feature Not Available

- Check browser compatibility (Chrome/Edge/Safari recommended)
- Ensure you're using HTTPS (required for microphone access)
- Check if microphone permissions are granted

## Future Enhancements

Potential improvements for future versions:

- [ ] Multi-language support
- [ ] Voice commands (e.g., "send message", "clear input")
- [ ] Offline speech recognition
- [ ] Voice response (text-to-speech)
- [ ] Custom wake words
- [ ] Voice activity detection improvements

## Code Examples

### Basic Usage

```javascript
import { voiceService } from './services/voiceService'

// Check if supported
if (voiceService.checkSupport()) {
  // Start listening
  voiceService.startListening()
  
  // Handle results
  voiceService.onResult((result) => {
    if (result.final) {
      console.log('Final transcript:', result.final)
    } else {
      console.log('Interim transcript:', result.interim)
    }
  })
  
  // Handle errors
  voiceService.onError((error) => {
    console.error('Voice error:', error)
  })
}
```

### Integration in React Component

```javascript
const [isListening, setIsListening] = useState(false)

useEffect(() => {
  voiceService.onStart(() => setIsListening(true))
  voiceService.onEnd(() => setIsListening(false))
  
  return () => {
    if (voiceService.getListeningState()) {
      voiceService.stopListening()
    }
  }
}, [])

const handleVoiceToggle = () => {
  if (isListening) {
    voiceService.stopListening()
  } else {
    voiceService.startListening()
  }
}
```

## Testing

To test the voice input feature:

1. Open the chat page
2. Click the microphone button
3. Grant microphone permission
4. Speak a test message: "My computer is slow"
5. Verify the text appears in the input field
6. Send the message and verify it works

## Known Limitations

1. **Browser Support** - Only works in Chrome/Edge/Safari
2. **Internet Required** - Some browsers use cloud recognition
3. **Language** - Currently supports English (en-US) only
4. **Accuracy** - Depends on microphone quality and environment
5. **Privacy** - Audio may be sent to cloud services (browser-dependent)

## Support

For issues or questions:
- Check browser console for error messages
- Verify microphone permissions
- Test in Chrome/Edge for best compatibility
- Review this documentation for troubleshooting steps

---

**Last Updated:** 2025-01-27  
**Feature Status:** ✅ Implemented and Ready for Use

