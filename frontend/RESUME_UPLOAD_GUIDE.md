# Resume Upload & Parsing Feature

## 📄 How It Works

The Resume Upload feature allows users to upload their CV/resume and automatically extract key information to populate their Career Compass AI profile.

### **Supported File Types:**
- ✅ PDF files (.pdf)
- ✅ Text files (.txt)
- ✅ Word documents (.doc, .docx)

### **Information Extracted:**
1. **Name** - Full name of the candidate
2. **Experience** - Years of experience or experience summary
3. **Skills** - Technical and professional skills
4. **Last 2 Job Titles** - Most recent job positions

## 🎯 **User Experience Flow:**

### **Step 1: Upload Resume**
1. Navigate to Dashboard
2. Find "📄 Upload Your Resume" section at the top
3. Click "Choose Resume File" button
4. Select your resume file (PDF, DOC, DOCX, or TXT)

### **Step 2: Parse Resume**
1. After selecting file, click "Parse Resume" button
2. System processes the file and extracts information
3. Loading indicator shows "Parsing..." status

### **Step 3: View Extracted Profile**
1. Parsed information appears in "👤 Your Profile Summary" section
2. Shows: Name, Experience, Recent Job Titles, Key Skills
3. Skills are displayed as colored tags for easy reading

### **Step 4: Auto-Fill Career Tools**
- Extracted information automatically populates career planning forms
- Job title, experience, and skills are pre-filled
- Users can modify or enhance the information as needed

## 🛠️ **Technical Implementation:**

### **Frontend (Dashboard):**
- File upload component with drag-and-drop support
- Progress indicators for upload and parsing
- Responsive profile display section
- Auto-fill integration with existing career tools

### **Backend (API Route):**
- `/api/parse-resume` endpoint
- Handles multiple file formats
- Text extraction and AI-powered parsing
- Returns structured JSON with extracted data

### **Parsing Algorithm:**
- **Name Detection**: Regex patterns for common name formats
- **Experience Extraction**: Pattern matching for "X years of experience"
- **Skills Identification**: Technical skills dictionary matching
- **Job Title Extraction**: Common job title patterns and date associations

## 📋 **Sample Output:**

```json
{
  "profile": {
    "name": "John Smith",
    "experience": "5 years of experience in full-stack development",
    "skills": ["JavaScript", "React", "Node.js", "Python", "AWS"],
    "lastTwoJobs": ["Senior Software Engineer", "Software Developer"]
  }
}
```

## 🔮 **Future Enhancements:**

### **Production Ready Features:**
- **PDF Parsing**: Integration with `pdf-parse` library
- **Word Document Support**: Using `mammoth.js` for DOCX files
- **AI-Powered Extraction**: OpenAI API for more accurate parsing
- **Resume Templates**: Support for various resume formats
- **Data Validation**: Smart validation of extracted information

### **Advanced Features:**
- **Education Extraction**: Degree, university, graduation year
- **Contact Information**: Email, phone, LinkedIn profile
- **Certifications**: Professional certifications and courses
- **Language Skills**: Spoken and programming languages
- **Project History**: Key projects and achievements

## 🔧 **Installation & Setup:**

### **Required Dependencies:**
```bash
npm install pdf-parse mammoth
```

### **For Text Files:**
```javascript
// Already supported - no additional setup needed
```

### **For PDF Files:**
```javascript
import pdfParse from 'pdf-parse';
const buffer = await file.arrayBuffer();
const data = await pdfParse(buffer);
const text = data.text;
```

### **For Word Documents:**
```javascript
import mammoth from 'mammoth';
const buffer = await file.arrayBuffer();
const result = await mammoth.extractRawText({ buffer });
const text = result.value;
```

## ✅ **Testing the Feature:**

1. **Upload Sample Resume**: Use the demo data or upload your own
2. **Verify Parsing**: Check that information is correctly extracted
3. **Test Auto-Fill**: Ensure career tools are populated with parsed data
4. **Validate Display**: Confirm profile summary shows correctly

## 🎉 **Benefits:**

- ⚡ **Fast Setup**: Users can quickly populate their profile
- 🎯 **Accurate Data**: Reduces manual entry errors
- 🔄 **Seamless Integration**: Auto-fills all career planning tools
- 📊 **Better Insights**: More complete profile data for AI recommendations

The resume upload feature significantly improves user onboarding and provides a seamless way to get started with Career Compass AI's personalized career planning tools. 