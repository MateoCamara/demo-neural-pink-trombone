/*
    TODO
        Toggle phonemes (voice/voiceless/none)
        refactor button creation
*/

class ButtonsUI {
    constructor() {
        this._container = document.createElement("div");
        this._container.style.display = "grid";
        this._container.style.flexDirection = "column";
        this._container.style.position = "absolute";
        this._container.style.top = "0";
        this._container.style.right = "0";

        this._buttons = {
            start: this._createButton("start"),
            voice: this._createButton("voice", true, "intensity"),
            stfu: this._createButton('stfu', false, 'stfu'),
            // roy: this._createButton('roy', false, 'roy'),
            // equal: this._createButton('equal', false, 'equal'),
            // yawn1: this._createButton('yawn1', false, 'yawn1'),
            // // wobble : this._createButton("wobble", true, "vibrato.wobble"),
            // // loop: this._createButton("loop", true, "loop"),
            // aeiou: this._createButton('aeiou', false, 'aeiou'),
            // ao: this._createButton('ao', false, 'ao'),
            // a_f: this._createButton('a_f', false, 'a_f'),
            // eiu: this._createButton('eiu', false, 'eiu'),
            // roy_f: this._createButton('roy_f', false, 'roy_f'),
            // u_f: this._createButton('u_f', false, 'u_f'),
            // yawn1_1: this._createButton('yawn1_1', false, 'yawn1_1'),
            // yawn1_2: this._createButton('yawn1_2', false, 'yawn1_2'),
            // yawn1_3: this._createButton('yawn1_3', false, 'yawn1_3'),
            // yawn1_4: this._createButton('yawn1_4', false, 'yawn1_4'),
            // yawn2_1: this._createButton('yawn2_1', false, 'yawn2_1'),
            // yawn2_2: this._createButton('yawn2_2', false, 'yawn2_2'),
            // yawn2_3: this._createButton('yawn2_3', false, 'yawn2_3'),
            // yawn2_4: this._createButton('yawn2_4', false, 'yawn2_4'),
            // yawn3_1: this._createButton('yawn3_1', false, 'yawn3_1'),
            // yawn3_2: this._createButton('yawn3_2', false, 'yawn3_2'),
            // yawn3_3: this._createButton('yawn3_3', false, 'yawn3_3'),
            // yawn3_4: this._createButton('yawn3_4', false, 'yawn3_4'),

        };

        this._buttons.start.addEventListener("didResume", event => {
            event.target.parentElement.removeChild(event.target);
        });
        this._buttons.start.addEventListener("click", event => {
            event.target.dispatchEvent(new CustomEvent("resume", {
                bubbles: true,
            }));

        });
    }

    get node() {
        return this._container;
    }

    _createButton(buttonName, isParameter = false, parameterPath) {
        const button = document.createElement("button");
        button.id = buttonName;
        button.value = true;
        button.innerText = (isParameter ? "disable" : '') + buttonName;
        button.style.width = "100%";
        button.style.flex = 1;
        button.style.margin = "2px";
        button.style.borderRadius = "20px";
        button.style.backgroundColor = "pink";
        button.style.border = "solid red";
        this._container.appendChild(button);

        if (isParameter) {
            button.addEventListener("click", event => {
                button.value = (button.value == "false");

                const prefix = (button.value == "true") ?
                    "disable" :
                    "enable";
                button.innerText = prefix + ' ' + button.id;

                button.dispatchEvent(new CustomEvent("setParameter", {
                    bubbles: true,
                    detail: {
                        parameterName: parameterPath || buttonName,
                        newValue: (button.value == "true") ? 1 : 0,
                    }
                }));

                button.dispatchEvent(new CustomEvent("message", {
                    bubbles: true,
                    detail: {
                        type: "toggleButton",
                        parameterName: buttonName,
                        newValue: button.value,
                    }
                }));
            });
        } else {
            if (buttonName == 'start') return button;

            button.addEventListener("click", event => {

                button.dispatchEvent(new CustomEvent(buttonName, {
                    bubbles: true,
                    detail: {
                        parameterName: parameterPath || buttonName,
                        newValue: (button.value == "true") ? 1 : 0,
                    }
                }));

                button.dispatchEvent(new CustomEvent("message", {
                    bubbles: true,
                    detail: {
                        type: "toggleButton",
                        parameterName: buttonName,
                        newValue: button.value,
                    }
                }));
            });

        }
        return button;
    }
}

export default ButtonsUI;