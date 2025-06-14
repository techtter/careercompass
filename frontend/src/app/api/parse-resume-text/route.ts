import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

export async function POST(request: NextRequest) {
  try {
    // Authenticate the user
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get the resume text from request body
    const { resumeText } = await request.json();
    
    if (!resumeText || typeof resumeText !== 'string' || resumeText.trim().length === 0) {
      return NextResponse.json({ error: 'No resume text provided' }, { status: 400 });
    }

    // Parse resume using the same AI parsing function
    const profile = await parseResumeWithAI(resumeText.trim());

    return NextResponse.json({ 
      success: true, 
      profile,
      message: 'Resume text parsed successfully' 
    });

  } catch (error) {
    console.error('Error parsing resume text:', error);
    return NextResponse.json(
      { error: 'Failed to parse resume text' }, 
      { status: 500 }
    );
  }
}

async function parseResumeWithAI(resumeText: string) {
  // Extract name (simple pattern - first line or after "Name:")
  let name = extractName(resumeText);
  
  // Extract experience
  let experience = extractExperience(resumeText);
  
  // Extract skills
  let skills = extractSkills(resumeText);
  
  // Extract last two job titles
  let lastTwoJobs = extractJobTitles(resumeText);

  return {
    name: name || 'Name not found',
    experience: experience || 'Experience not specified',
    skills: skills || ['Skills not found'],
    lastTwoJobs: lastTwoJobs || ['Job titles not found']
  };
}

function extractName(text: string): string {
  // Look for name patterns
  const namePatterns = [
    /^([A-Z][a-z]+ [A-Z][a-z]+)/m,
    /Name[:\s]+([A-Za-z\s]+)/i,
    /^([A-Z][A-Z\s]+)/m
  ];
  
  for (const pattern of namePatterns) {
    const match = text.match(pattern);
    if (match && match[1]) {
      return match[1].trim();
    }
  }
  
  // Fallback: first line if it looks like a name
  const firstLine = text.split('\n')[0]?.trim();
  if (firstLine && /^[A-Za-z\s]{2,50}$/.test(firstLine)) {
    return firstLine;
  }
  
  return 'Name not found';
}

function extractExperience(text: string): string {
  // Look for experience patterns
  const expPatterns = [
    /(\d+\+?\s*years?\s*of\s*experience)/i,
    /experience[:\s]+([^\n]+)/i,
    /(\d+\+?\s*years?\s*in)/i
  ];
  
  for (const pattern of expPatterns) {
    const match = text.match(pattern);
    if (match && match[1]) {
      return match[1].trim();
    }
  }
  
  // Count work experiences as rough estimate
  const jobCount = (text.match(/\b(software engineer|developer|manager|analyst|consultant|designer)\b/gi) || []).length;
  if (jobCount > 0) {
    return `Approximately ${jobCount} relevant positions found`;
  }
  
  return 'Experience details not found';
}

function extractSkills(text: string): string[] {
  // Common technical skills
  const skillPatterns = [
    // Programming languages
    /\b(JavaScript|TypeScript|Python|Java|C\+\+|C#|Ruby|PHP|Go|Rust|Swift|Kotlin)\b/gi,
    // Frameworks
    /\b(React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|Laravel|Rails)\b/gi,
    // Databases
    /\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server)\b/gi,
    // Cloud & DevOps
    /\b(AWS|Azure|Google Cloud|Docker|Kubernetes|Jenkins|Git|CI\/CD)\b/gi,
    // Other tech
    /\b(HTML|CSS|SCSS|Tailwind|Bootstrap|REST|GraphQL|API|Microservices)\b/gi
  ];
  
  const skills = new Set<string>();
  
  for (const pattern of skillPatterns) {
    const matches = text.match(pattern);
    if (matches) {
      matches.forEach(skill => skills.add(skill));
    }
  }
  
  // Look for skills sections with enhanced delimiter support
  const skillsSection = text.match(/skills[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)/i);
  if (skillsSection) {
    const skillsText = skillsSection[1];
    const extractedSkills = skillsText
      .split(/[,\/\|\;\n•\-\+\*]/)  // Added slash, pipe, semicolon support
      .map(s => s.trim())
      .filter(s => s.length > 2 && s.length < 50 && !['and', 'etc', 'more'].includes(s.toLowerCase()));
    
    extractedSkills.forEach(skill => skills.add(skill));
  }
  
  // Also look for multi-line skills sections
  const lines = text.split('\n');
  let inSkillsSection = false;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim().toLowerCase();
    
    if (line.includes('skills') || line.includes('technologies')) {
      inSkillsSection = true;
      continue;
    }
    
    if (inSkillsSection && (line.includes('experience') || line.includes('education') || line.includes('work'))) {
      break;
    }
    
    if (inSkillsSection && lines[i].trim()) {
      const skillLine = lines[i].trim();
      // Remove bullet points and split by delimiters
      const cleanLine = skillLine.replace(/^[•◦\-\*\+]\s*/, '');
      const lineSkills = cleanLine
        .split(/[,\/\|\;]/)  // Split by comma, slash, pipe, semicolon
        .map(s => s.trim())
        .filter(s => s.length > 2 && s.length < 50 && !['and', 'etc', 'more'].includes(s.toLowerCase()));
      
      lineSkills.forEach(skill => skills.add(skill));
    }
  }
  
  return Array.from(skills).slice(0, 15); // Limit to 15 skills
}

function extractJobTitles(text: string): string[] {
  // Common job title patterns
  const titlePatterns = [
    /\b(Senior|Junior|Lead|Principal)?\s*(Software Engineer|Developer|Programmer|Analyst|Manager|Director|Consultant|Designer|Architect)\b/gi,
    /\b(Full[- ]?Stack|Frontend|Backend|DevOps|Data|Mobile|Web)\s*(Developer|Engineer)\b/gi
  ];
  
  const titles = new Set<string>();
  
  for (const pattern of titlePatterns) {
    const matches = text.match(pattern);
    if (matches) {
      matches.forEach(title => titles.add(title.trim()));
    }
  }
  
  // Look for experience sections with dates
  const experienceMatches = text.match(/(\d{4}[\s\-]+\d{4}|\d{4}[\s\-]+present).*?([^\n]+)/gi);
  if (experienceMatches) {
    experienceMatches.forEach(exp => {
      const titleMatch = exp.match(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g);
      if (titleMatch) {
        titleMatch.forEach(title => {
          if (title.length > 5 && title.length < 50) {
            titles.add(title);
          }
        });
      }
    });
  }
  
  return Array.from(titles).slice(0, 2); // Return last 2 job titles
} 