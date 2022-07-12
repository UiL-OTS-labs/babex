<!-- Retrieves Django's CSRF token from cookie, to be used in forms -->
<script lang="ts" setup>
    function getCookie(name: string) : string | null {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');
</script>

<template>
  <input type="hidden" name="csrfmiddlewaretoken" :value="csrftoken">
</template>
