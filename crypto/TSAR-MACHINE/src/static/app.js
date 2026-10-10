document.addEventListener('DOMContentLoaded', () => {
    const keyboardGrid = document.getElementById('keyboardGrid');
    const paperText = document.getElementById('paperText');
    const paperSheet = document.getElementById('paperSheet');
    const responseContainer = document.getElementById('responseContainer');
    const responseText = document.getElementById('responseText');
    const transmitBtn = document.getElementById('transmitBtn');
    const feedNewPaperBtn = document.getElementById('feedNewPaperBtn');
    const carriageLever = document.getElementById('carriageLever');
    
    const lampPower = document.getElementById('lampPower');
    const lampTransmit = document.getElementById('lampTransmit');
    const lampParity = document.getElementById('lampParity');

    // Turn on power lamp
    lampPower.classList.add('active');

    let currentText = '';
    let rawInputText = ''; // Accumulates exact key strikes for raw triplet verification
    let lineCharCount = 0;
    let pendingTriplet = []; // Holds characters for the current non-overlapping group of 3
    const BELL_MARGIN = 45; // Ring bell when approaching end of line

    // Typewriter layout configuration (vintage QWERTY layout with separate digits row and functional keys)
    const keyboardLayout = [
        // Number row
        [
            { char: '1', sub: '!' },
            { char: '2', sub: '@' },
            { char: '3', sub: '#' },
            { char: '4', sub: '$' },
            { char: '5', sub: '%' },
            { char: '6', sub: '^' },
            { char: '7', sub: '&' },
            { char: '8', sub: '*' },
            { char: '9', sub: '(' },
            { char: '0', sub: ')' },
            { char: '-', sub: '_' },
            { char: '=', sub: '+' },
            { char: 'BKSP', action: 'backspace', class: 'key-wide' }
        ],
        // Top Letter Row
        [
            { char: 'TAB', action: 'tab', class: 'key-wide' },
            { char: 'Q' }, { char: 'W' }, { char: 'E' }, { char: 'R' }, { char: 'T' },
            { char: 'Y' }, { char: 'U' }, { char: 'I' }, { char: 'O' }, { char: 'P' },
            { char: '[' }, { char: ']' }
        ],
        // Home Letter Row
        [
            { char: 'A' }, { char: 'S' }, { char: 'D' }, { char: 'F' }, { char: 'G' },
            { char: 'H' }, { char: 'J' }, { char: 'K' }, { char: 'L' },
            { char: ';' }, { char: "'" },
            { char: 'RETURN', action: 'enter', class: 'key-wide' }
        ],
        // Bottom Letter Row
        [
            { char: 'SHIFT', action: 'shift', class: 'key-wide' },
            { char: 'Z' }, { char: 'X' }, { char: 'C' }, { char: 'V' }, { char: 'B' },
            { char: 'N' }, { char: 'M' }, { char: ',' }, { char: '.' }, { char: '/' },
            { char: 'CLEAR', action: 'clear', class: 'key-wide' }
        ],
        // Spacebar Row
        [
            { char: 'SPACE', action: 'space', class: 'key-space' }
        ]
    ];

    let shiftActive = false;

    // Build interactive keyboard DOM
    const keyElementMap = {};

    keyboardLayout.forEach(row => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'key-row';

        row.forEach(keyConfig => {
            const keyBtn = document.createElement('div');
            keyBtn.className = 'type-key' + (keyConfig.class ? ' ' + keyConfig.class : '');
            
            const innerDiv = document.createElement('div');
            innerDiv.className = 'key-inner';

            if (keyConfig.sub) {
                const subSpan = document.createElement('span');
                subSpan.className = 'key-sub';
                subSpan.textContent = keyConfig.sub;
                innerDiv.appendChild(subSpan);
            }

            const charSpan = document.createElement('span');
            charSpan.className = 'key-char';
            charSpan.textContent = keyConfig.char;
            innerDiv.appendChild(charSpan);

            keyBtn.appendChild(innerDiv);

            // Click / Touch listener
            keyBtn.addEventListener('click', (e) => {
                e.preventDefault();
                handleKeyPress(keyConfig);
                animateKey(keyBtn);
            });

            // Map for physical keyboard lookup
            const lookupKey = (keyConfig.char || '').toUpperCase();
            if (!keyElementMap[lookupKey]) {
                keyElementMap[lookupKey] = keyBtn;
            }
            if (keyConfig.action) {
                keyElementMap[keyConfig.action.toUpperCase()] = keyBtn;
            }

            rowDiv.appendChild(keyBtn);
        });

        keyboardGrid.appendChild(rowDiv);
    });

    function animateKey(btn) {
        btn.classList.add('pressed');
        setTimeout(() => btn.classList.remove('pressed'), 100);
    }

    // Process character typing logic
    function handleKeyPress(config) {
        if (config.action) {
            switch (config.action) {
                case 'backspace':
                    if (currentText.length > 0) {
                        currentText = currentText.slice(0, -1);
                        lineCharCount = Math.max(0, lineCharCount - 1);
                        if (pendingTriplet.length > 0) {
                            pendingTriplet.pop();
                        }
                        if (rawInputText.length > 0) {
                            rawInputText = rawInputText.slice(0, -1);
                        }
                        window.soundEngine.playKeyStrike();
                    }
                    break;
                case 'enter':
                    currentText += '\n';
                    lineCharCount = 0;
                    pendingTriplet = []; // Reset triplet on newline
                    window.soundEngine.playCarriageReturn();
                    break;
                case 'tab':
                    currentText += '    ';
                    lineCharCount += 4;
                    pendingTriplet = [];
                    window.soundEngine.playKeyStrike();
                    break;
                case 'space':
                    currentText += ' ';
                    lineCharCount++;
                    pendingTriplet = []; // Reset triplet on space separator
                    window.soundEngine.playKeyStrike();
                    break;
                case 'shift':
                    shiftActive = !shiftActive;
                    return;
                case 'clear':
                    currentText = '';
                    rawInputText = '';
                    lineCharCount = 0;
                    pendingTriplet = [];
                    responseContainer.style.display = 'none';
                    window.soundEngine.playCarriageReturn();
                    break;
            }
        } else {
            let charToAdd = config.char;
            if (shiftActive && config.sub) {
                charToAdd = config.sub;
                shiftActive = false; // single shift release
            } else if (!shiftActive && charToAdd.length === 1 && charToAdd >= 'A' && charToAdd <= 'Z') {
                charToAdd = charToAdd.toLowerCase();
            }

            rawInputText += charToAdd;
            pendingTriplet.push(charToAdd);
            window.soundEngine.playKeyStrike();

            if (pendingTriplet.length === 3) {
                // All 3 characters received: calculate average code value
                const code1 = pendingTriplet[0].charCodeAt(0);
                const code2 = pendingTriplet[1].charCodeAt(0);
                const code3 = pendingTriplet[2].charCodeAt(0);

                const avgCode = Math.round((code1 + code2 + code3) / 3);
                const mergedChar = String.fromCharCode(avgCode);

                // Replace the 2 temporarily displayed characters with the 1 merged character
                currentText = currentText.slice(0, -2) + mergedChar;
                lineCharCount = Math.max(0, lineCharCount - 1);

                // Discard triplet so the merged character is never part of the next triplet!
                pendingTriplet = [];

                // Sound feedback for the mechanical contraction
                window.soundEngine.playKeyStrike();
            } else {
                // 1st or 2nd character: print temporarily on paper
                currentText += charToAdd;
                lineCharCount++;
            }

            // Margin warning bell
            if (lineCharCount === BELL_MARGIN) {
                window.soundEngine.playBell();
            }
        }

        updatePaper();
    }

    function updatePaper() {
        paperText.textContent = currentText;
        paperSheet.scrollTop = paperSheet.scrollHeight;
    }

    // Physical keyboard bridge (allows seamless typing with real keyboard)
    window.addEventListener('keydown', (e) => {
        // Prevent page scrolling on Space / Backspace
        if (e.key === ' ' || e.key === 'Backspace' || e.key === 'Tab') {
            e.preventDefault();
        }

        const key = e.key;
        let mappedConfig = null;

        if (key === 'Backspace') {
            mappedConfig = { action: 'backspace' };
            animateKey(keyElementMap['BACKSPACE'] || keyElementMap['BKSP']);
        } else if (key === 'Enter') {
            mappedConfig = { action: 'enter' };
            animateKey(keyElementMap['ENTER'] || keyElementMap['RETURN']);
        } else if (key === 'Tab') {
            mappedConfig = { action: 'tab' };
            animateKey(keyElementMap['TAB']);
        } else if (key === ' ') {
            mappedConfig = { action: 'space' };
            animateKey(keyElementMap['SPACE']);
        } else if (key.length === 1) {
            mappedConfig = { char: key };
            const uppercaseChar = key.toUpperCase();
            if (keyElementMap[uppercaseChar]) {
                animateKey(keyElementMap[uppercaseChar]);
            }
        }

        if (mappedConfig) {
            handleKeyPress(mappedConfig);
        }
    });

    // Carriage Return Lever
    carriageLever.addEventListener('click', () => {
        carriageLever.classList.add('pulled');
        window.soundEngine.playCarriageReturn();
        currentText += '\n';
        lineCharCount = 0;
        updatePaper();
        setTimeout(() => carriageLever.classList.remove('pulled'), 200);
    });

    // Feed New Paper button
    feedNewPaperBtn.addEventListener('click', () => {
        window.soundEngine.playCarriageReturn();
        currentText = '';
        rawInputText = '';
        pendingTriplet = [];
        lineCharCount = 0;
        responseContainer.style.display = 'none';
        responseText.textContent = '';
        updatePaper();
    });

    // Ribbon ink color toggle (pure visual detail)
    const ribbonSwitch = document.querySelector('.ribbon-color-switch');
    if (ribbonSwitch) {
        ribbonSwitch.addEventListener('click', () => {
            const dots = ribbonSwitch.querySelectorAll('.color-dot');
            dots.forEach(d => d.classList.toggle('active'));
            paperText.classList.toggle('red-mode');
            window.soundEngine.playKeyStrike();
        });
    }

    // Transmit & Query /api/process endpoint
    transmitBtn.addEventListener('click', async () => {
        if (!rawInputText.trim()) {
            return;
        }

        lampTransmit.classList.add('active');
        transmitBtn.disabled = true;

        try {
            const res = await fetch('/api/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    raw_input: rawInputText,
                    input: currentText
                })
            });

            const data = await res.json();

            // Display response on paper
            responseContainer.style.display = 'block';
            responseText.textContent = data.output || JSON.stringify(data, null, 2);

            // Toggle parity lamp green on full success or amber/red on partial
            if (data.all_matched) {
                lampParity.classList.add('active');
                window.soundEngine.playBell();
                setTimeout(() => window.soundEngine.playBell(), 200);
            } else {
                lampParity.classList.remove('active');
                window.soundEngine.playBell();
            }

            paperSheet.scrollTop = paperSheet.scrollHeight;

        } catch (err) {
            responseContainer.style.display = 'block';
            responseText.textContent = '[TRANSMISSION FAILURE]: Could not reach central cipher gears.';
        } finally {
            setTimeout(() => lampTransmit.classList.remove('active'), 500);
            transmitBtn.disabled = false;
        }
    });
});
