
<nav id='nav'>
  <h1 class='title'>STI Transition Visualizer</h1> 

  <div class='buttons'>
    <button disabled='{!STIbase64}'>
      <a href='{STIbase64}' download='STI.png'>Save STI</a>
    </button>

    <button
      on:click='{requestVideo}'
      class:ghost='{STIbase64}'>
        Upload a New Video
    </button>

    <button on:click='{() => settingsOpen = !settingsOpen}' class='grey'>
      Settings
    </button>
  </div>
</nav>

<div class='pointer' class:hidden={!hovering} bind:this={pointer}>{curFrame}</div>
<div id='STI-editor' hidden={!STIbase64}>
  <div class='scrubber'>
    <img id='sti_target' alt='sti' 
      bind:this={STITarg}
      on:mousemove={scrubImage}
      on:mouseleave={scrubEnd}  
    />
  </div>
</div>

<div id='toolbar'>
  <div style='width: 100%; text-align: center; position: relative;'>
    <div class='frame'>Frame {curFrame} / {frameCount}</div>
    <div class='label'>STI ({type}, {dir})</div>
    <div class='orig'>
      <label>
        <input type='checkbox' bind:checked={maintainSize}/>
        Maintain original size
      </label>
    </div>
  </div>
</div>

{#if checking}
<div id='loading-overlay' 
  class='bg-overlay'>
  <span>Generating new STI...</span>
</div>
{/if}

{#if settingsOpen}
<div id='settings-overlay'
  class='bg-overlay'>
  <div>
    <h1>Settings</h1>

    <form on:submit|preventDefault={() => { processVideo(); settingsOpen = false}}>
      <label><strong>STI Type</strong></label>
      <select bind:value={type}>
        <option selected value='raw'>Raw Pixels</option>
        <option value='hist'>Histogram Intersection</option>
      </select>

      <br/>

      <label><strong>Copy Direction</strong></label>
      <select bind:value={dir}>
        <option selected value='rows'>By Rows</option>
        <option value='cols'>By Columns</option>
      </select>

      <div style='display: flex; width: 100%; padding: 2rem 0 1rem;'>
        <button type='submit'>Save {(STIbase64) ? '& Generate STI' : ''}</button>
        <button style='background: none; color: inherit;' on:click={() => settingsOpen = false}>Cancel</button>
      </div>
    </form>
  </div>
</div>
{/if}

<style type='text/sass'>
  #loading-overlay {
    padding: 3rem;
    text-align: right;

    span {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      flex: 0;

      &::before {
        content: '';
        margin-right: 1rem;
        display: inline-block;
        width: 1.8rem;
        height: 1.8rem;

        background: conic-gradient(
          from 90deg, 
          rgba(white, 0), 
          rgba(white, 0.7)
        );
        border-radius: 100%;

        @keyframes rotate { 
          from { transform: rotate(0deg);}
          to { transform: rotate(360deg); }
        }
        animation: rotate 1.5s linear infinite;
      }
    }
  }

  #settings-overlay {
    display: flex;
    justify-content: center;
    align-items: center;

    div {
      padding: 2rem;
      width: 50%;

      background: white;
      color: #202020;
    }
  }

  #nav {
    width: 100%;
    padding: 1rem 2rem;

    display: flex;
    justify-content: space-between;
    align-items: baseline;
    position: fixed;
    top: 0; left: 0; right: 0;
    
    .title { font-size: 1.8rem; }
    .buttons > * { margin-left: 0.4rem; }
  }

  #STI-editor {
    width: 100%;
    position: absolute;
    top: 50%;
    transform: translate(0, -50%);

    text-align: center;
    overflow-x: auto;

    .scrubber {
      padding: 0 2rem;
      margin-bottom: 1rem;
      display: inline-block;
      width: 100%;
      height: 100px;

      position: relative;

      img { 
        object-fit: fill;
        width: 100%;
        height: 100%;
      }
    }
  }

  .pointer {
    padding: inherit;
    position: fixed;
    top: 0; left: 0;

    padding: 0.2rem 0.8rem;
    background: #E33333;
    border-radius: 100px;
    transform: translate(-5%, 0);

    &.hidden { opacity: 0; }
  }

  #toolbar {
    @extend #nav;
    top: auto; bottom: 0;

    flex-wrap: wrap;
    justify-content: center;
    padding-bottom: 1.4rem;

    .frame {
      position: absolute;
      top: 50%; left: 0;
      transform: translate(0, -50%);
    }

    .label {
      display: inline-block;
      padding: 0.4rem 0.6rem;
      background: rgba(white, 0.1);
      text-transform: capitalize;
    }

    .orig {
      position: absolute;
      top: 50%; right: 0;
      transform: translate(0, -50%);
    }
  }
</style>

<script>
  let checking = false
  let maintainSize = false
  let settingsOpen = false

  let pointer
  let STITarg, STIbase64 = null
  let file = null
  let frameCount = 0
  let STIoptions = {
    type: 'raw',
    dir: 'rows'
  }

  let type = 'raw', dir = 'rows'
  $: { STIoptions = { type, dir } }

  // Maintain original size
  $: {
    if (STITarg) {
      const size = (maintainSize) ? 'auto' : '100%'
      STITarg.style.width = size
      STITarg.style.height = size
      STITarg.parentElement.style.width = size
    }
  }

  async function requestVideo() {
    const newFile = await eel.requestVideoFile()()
    if (!newFile) return
    file = newFile
    processVideo()
  }

  async function processVideo() {
    if (file) checking = true
    const base64 = await eel.getSTI(file, STIoptions)()
    const count = await eel.getFrameCount(file)()
    checking = false
    if (!base64) return

    // set byte code to image
    frameCount = count
    STIbase64 = base64
    STITarg.src = STIbase64
  }

  let curFrame = 0
  let hovering = false
  function scrubImage(e) {
    hovering = true
    const width = e.currentTarget.offsetWidth
    const x_pos = e.offsetX
    curFrame = Math.max(Math.round((x_pos / width) * frameCount), 0)

    // Update Pointer
    const { left, top } = e.currentTarget.getBoundingClientRect()
    const { offsetWidth, offsetHeight } = pointer
    pointer.style.left = `${left + x_pos - (offsetWidth / 2)}px`
    pointer.style.top = `${top - offsetHeight - 12}px`
  }

  function scrubEnd() { hovering = false }
</script>