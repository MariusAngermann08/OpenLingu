// Handle platform tabs functionality
function initPlatformTabs() {
    const tabButtons = document.querySelectorAll('.platform-tab-btn');
    const tabContents = document.querySelectorAll('.platform-content');
    
    function updateCopyButtonsVisibility(activeContent) {
        // Hide all copy buttons in inactive tabs
        tabContents.forEach(content => {
            const copyBtns = content.querySelectorAll('.copy-btn');
            copyBtns.forEach(btn => {
                btn.style.opacity = '0';
                btn.style.transform = 'translateY(-5px)';
                btn.style.pointerEvents = 'none';
            });
        });
        
        // Show copy buttons in active tab
        if (activeContent) {
            const activeCopyBtns = activeContent.querySelectorAll('.copy-btn');
            activeCopyBtns.forEach(btn => {
                btn.style.opacity = '1';
                btn.style.transform = 'translateY(0)';
                btn.style.pointerEvents = 'auto';
            });
        }
    }
    
    function switchTab(event) {
        event.preventDefault();
        const platform = this.getAttribute('data-platform');
        
        // Update active state
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        this.classList.add('active');
        const activeContent = document.getElementById(platform + '-content');
        if (activeContent) {
            activeContent.classList.add('active');
            updateCopyButtonsVisibility(activeContent);
        }
    }
    
    tabButtons.forEach(button => {
        button.addEventListener('click', switchTab);
        // Add keyboard navigation
        button.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                switchTab(e);
            }
        });
    });
    
    // Initialize first tab if none is active
    const activeTab = document.querySelector('.platform-tab-btn.active');
    if (!activeTab && tabButtons.length > 0) {
        tabButtons[0].classList.add('active');
        const firstContent = document.getElementById(tabButtons[0].getAttribute('data-platform') + '-content');
        if (firstContent) {
            firstContent.classList.add('active');
            updateCopyButtonsVisibility(firstContent);
        }
    } else if (activeTab) {
        const activeContent = document.querySelector('.platform-content.active');
        if (activeContent) {
            updateCopyButtonsVisibility(activeContent);
        }
    }
    
    // Update copy buttons when hovering over tab content
    document.querySelectorAll('.platform-tab-content').forEach(content => {
        content.addEventListener('mouseenter', () => {
            const activeContent = content.querySelector('.platform-content.active');
            if (activeContent) {
                updateCopyButtonsVisibility(activeContent);
            }
        });
    });
}



// Initialize info toggle buttons
document.addEventListener('DOMContentLoaded', () => {
    const toggleButtons = document.querySelectorAll('.info-toggle');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            const expanded = button.getAttribute('aria-expanded') === 'true' || false;
            button.setAttribute('aria-expanded', !expanded);
            button.closest('.info-banner').setAttribute('aria-expanded', !expanded);
        });
    });
});

// Initialize copy buttons for code blocks
function initCopyButtons() {
    // Remove any existing event listeners first to prevent duplicates
    document.querySelectorAll('.copy-btn').forEach(btn => {
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
    });
    
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    if (!copyButtons.length) {
        console.warn('No copy buttons found');
        return;
    }
    
    console.log('Initializing', copyButtons.length, 'copy buttons');
    
    // Split code into lines and wrap each line for animation
    function prepareCodeLines(codeBlock) {
        const pre = codeBlock.querySelector('pre');
        if (!pre) return;
        
        const code = pre.querySelector('code');
        if (!code) return;
        
        // Split content into lines and wrap each line
        const lines = code.innerHTML.split('\n');
        const wrappedLines = lines.map((line, index) => {
            if (line.trim() === '') return '';
            return `<span class="code-line" style="--line-index: ${index}">${line}</span>`;
        }).join('\n');
        
        code.innerHTML = wrappedLines;
    }
    
    // Initialize code line wrapping
    document.querySelectorAll('.code-block').forEach(block => {
        prepareCodeLines(block);
    });
    
    // Handle copy button click
    function handleCopyClick(event) {
        event.preventDefault();
        event.stopPropagation();
        
        const button = event.currentTarget;
        if (button.classList.contains('copying')) return;
        
        button.classList.add('copying');
        const codeBlock = button.closest('.code-block');
        const codeElement = codeBlock.querySelector('pre code');
        const code = codeElement.textContent;
        
        // Add copied class to trigger animations
        codeBlock.classList.add('copied');
        
        // Remove the class after animation completes
        setTimeout(() => {
            codeBlock.classList.add('fade-out');
            // Remove the classes after fade out completes
            setTimeout(() => {
                codeBlock.classList.remove('copied', 'fade-out');
            }, 500);
        }, 1500);
        
        // Create ripple effect
        const ripple = document.createElement('span');
        ripple.className = 'copy-ripple';
        button.appendChild(ripple);
        
        // Remove ripple after animation
        setTimeout(() => {
            ripple.remove();
        }, 600);
        
        // Check if the browser supports the Clipboard API
        const copyPromise = navigator.clipboard 
            ? navigator.clipboard.writeText(code)
            : new Promise((resolve) => {
                // Fallback for older browsers
                const textarea = document.createElement('textarea');
                textarea.value = code;
                textarea.style.position = 'fixed';
                document.body.appendChild(textarea);
                textarea.select();
                
                try {
                    const successful = document.execCommand('copy');
                    document.body.removeChild(textarea);
                    if (successful) {
                        resolve();
                    } else {
                        throw new Error('Copy command was unsuccessful');
                    }
                } catch (err) {
                    document.body.removeChild(textarea);
                    throw err;
                }
            });
        
        copyPromise
            .then(() => {
                // Success state
                button.classList.add('copied');
                button.setAttribute('aria-label', 'Copied!');
                
                // Change icon to checkmark
                const icon = button.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-check';
                }
                
                // Reset after delay
                setTimeout(() => {
                    button.classList.remove('copied', 'copying');
                    button.setAttribute('aria-label', 'Copy to clipboard');
                    if (icon) {
                        icon.className = 'far fa-copy';
                    }
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
                // Show error state
                button.classList.add('error');
                const icon = button.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-times';
                }
                
                setTimeout(() => {
                    button.classList.remove('error', 'copying');
                    if (icon) {
                        icon.className = 'far fa-copy';
                    }
                }, 1500);
            });
    }
    
    // Add click event listeners to all copy buttons
    copyButtons.forEach(button => {
        // Set initial ARIA attributes for accessibility
        button.setAttribute('aria-label', 'Copy to clipboard');
        button.setAttribute('role', 'button');
        button.setAttribute('tabindex', '0');
        
        // Add click handler
        button.addEventListener('click', handleCopyClick);
        
        // Add keyboard support
        button.addEventListener('keydown', (e) => {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                handleCopyClick(e);
            }
        });
    });
}

// Initialize everything when DOM is loaded
function init() {
    console.log('Initializing...');
    
    // Initialize platform tabs if they exist on the page
    if (document.querySelector('.platform-tab-btn')) {
        initPlatformTabs();
    }
    
        // Initialize copy buttons after a small delay to ensure DOM is ready
    setTimeout(() => {
        initCopyButtons();
        
        // Re-initialize copy buttons after tab switch
        const tabButtons = document.querySelectorAll('.platform-tab-btn');
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Small delay to ensure tab content is visible
                setTimeout(initCopyButtons, 50);
            });
        });
    }, 100);
    
    // Handle loading screen
    const loadingScreen = document.querySelector('.loading-screen');
    if (loadingScreen) {
        // Remove loading screen after page is fully loaded
        window.addEventListener('load', function() {
            document.body.classList.remove('loading');
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 500);
        });
    }
    
    console.log('Initialization complete');
}

// Initialize role sections
function initRoleSections() {
    const roleSections = document.querySelectorAll('.role-section');
    if (!roleSections.length) return;

    // Function to handle role section toggling
    function toggleRoleSection(header) {
        const section = header.closest('.role-section');
        const isActive = section.classList.contains('active');
        
        // Close all sections first
        roleSections.forEach(s => {
            s.classList.remove('active');
            const content = s.querySelector('.role-content');
            content.style.maxHeight = null;
        });
        
        // If the clicked section wasn't active, open it
        if (!isActive) {
            section.classList.add('active');
            const content = section.querySelector('.role-content');
            content.style.maxHeight = content.scrollHeight + 'px';
        }
    }

    // Add click handlers to role headers
    roleSections.forEach((section, index) => {
        const header = section.querySelector('.role-header');
        const content = section.querySelector('.role-content');
        
        // Make header focusable and add keyboard support
        header.setAttribute('tabindex', '0');
        header.setAttribute('role', 'button');
        header.setAttribute('aria-expanded', 'false');
        
        header.addEventListener('click', () => toggleRoleSection(header));
        
        header.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleRoleSection(header);
            }
        });
        
        // Update ARIA attributes on toggle
        section.addEventListener('transitionend', () => {
            const isActive = section.classList.contains('active');
            header.setAttribute('aria-expanded', isActive.toString());
        });
        
        // Set initial state (first one open by default)
        if (index === 0) {
            section.classList.add('active');
            content.style.maxHeight = content.scrollHeight + 'px';
            header.setAttribute('aria-expanded', 'true');
        } else {
            content.style.maxHeight = null;
        }
    });
}

// Run when DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        init();
        initRoleSections();
        initCopyButtons();
        initPlatformTabs();
        initInfoToggles();
        initComponentCards();
    });
} else {
    init();
    initRoleSections();
}

// Initialize component cards with hover effects
function initComponentCards() {
    const cards = document.querySelectorAll('.component-card');
    
    // Make sure links are properly handled within cards
    cards.forEach(card => {
        const links = card.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        });
    });
}

// Smooth scroll to anchor links
function smoothScrollToAnchor() {
    if (window.location.hash) {
        const target = document.querySelector(window.location.hash);
        if (target) {
            setTimeout(() => {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    }
}

// Add smooth page transitions
document.addEventListener('DOMContentLoaded', function() {
    // Set smooth scrolling for the whole document
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Remove loading class and show content with animation
    const loadingScreen = document.querySelector('.loading-screen');
    if (loadingScreen) {
        loadingScreen.style.opacity = '0';
        loadingScreen.style.visibility = 'hidden';
        loadingScreen.style.transition = 'opacity 0.5s ease, visibility 0.5s ease';
        
        // Remove loading screen from DOM after animation
        setTimeout(() => {
            loadingScreen.remove();
            // Add visible class to trigger page transition in
            document.body.classList.add('page-transition', 'visible');
            // Scroll to anchor if present
            smoothScrollToAnchor();
        }, 500);
    } else {
        // If no loading screen, still add the transition class
        setTimeout(() => {
            document.body.classList.add('page-transition', 'visible');
            smoothScrollToAnchor();
        }, 50);
    }
    
    // Add hover effects to interactive elements
    const interactiveElements = [
        'a:not(.no-hover)', 'button', '.endpoint', '.widget', '.feature',
        '.step', '.shortcut', 'pre', 'code',
        '.card', '.btn', '.tile', 'input[type="submit"]',
        'input[type="button"]', '.menu-item'
    ];
    
    interactiveElements.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => {
            el.style.transition = 'all 0.2s ease-in-out';
            
            el.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
            });
            
            el.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = 'none';
            });
        });
    });
    
    // Add animation to headings
    document.querySelectorAll('h1, h2, h3, h4').forEach((heading, index) => {
        heading.classList.add('fade-in-up');
        heading.style.animationDelay = `${index * 0.1}s`;
        
        // Trigger reflow
        void heading.offsetWidth;
        
        heading.style.opacity = '1';
        heading.style.transform = 'translateY(0)';
    });
    
    // Add animation to content sections
    document.querySelectorAll('section').forEach((section, index) => {
        section.classList.add('fade-in-up');
        section.style.animationDelay = `${0.3 + index * 0.1}s`;
        
        // Use Intersection Observer for scroll animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(section);
    });
});
