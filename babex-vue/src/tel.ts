import intlTelInput from 'intl-tel-input/intlTelInputWithUtils';
import 'intl-tel-input/build/css/intlTelInput.css';
import imgFlags from 'intl-tel-input/build/img/flags.webp';
import imgFlags2 from 'intl-tel-input/build/img/flags@2x.webp';
import imgGlobe from 'intl-tel-input/build/img/globe.webp';
import imgGlobe2 from 'intl-tel-input/build/img/globe@2x.webp';
// @ts-ignore
import { nl } from 'intl-tel-input/i18n';


export function init() {
    // initialize telephone input fields
    window.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('input[type="tel"]').forEach(input => {
            intlTelInput(input as HTMLInputElement,
                         {initialCountry: "nl",
                          i18n: nl,
                          strictMode: true});
        });
        let style = document.createElement('style');
        style.innerHTML = `
            .iti {
                --iti-path-flags-1x: url('${imgFlags}');
                --iti-path-flags-2x: url('${imgFlags2}');
                --iti-path-globe-1x: url('${imgGlobe}');
                --iti-path-globe-2x: url('${imgGlobe2}');
            }`;
        document.head.append(style);
    });
}
