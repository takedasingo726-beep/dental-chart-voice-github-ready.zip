(() => {

  const dropzone =
    document.getElementById("dropzone");

  const fileInput =
    document.getElementById("fileInput");

  const filenameLabel =
    document.getElementById("filename");

  const runButton =
    document.getElementById("runButton");

  const statusLine =
    document.getElementById("statusLine");

  const steps =
    document.querySelectorAll("#steps li");

  const emptyState =
    document.getElementById("emptyState");

  const karteForm =
    document.getElementById("karteForm");

  let selectedFile = null;
  let lastResult = null;


  function setStep(name) {

    steps.forEach((li) => {

      li.classList.toggle(
        "active",
        li.dataset.step === name
      );

    });

  }


  function setStatus(
    message,
    isError = false
  ) {

    statusLine.textContent = message;

    statusLine.classList.toggle(
      "error",
      isError
    );

  }


  ["dragover", "dragenter"].forEach(
    (evt) => {

      dropzone.addEventListener(
        evt,
        (e) => {

          e.preventDefault();

          dropzone.classList.add(
            "dragover"
          );

        }
      );

    }
  );


  ["dragleave", "drop"].forEach(
    (evt) => {

      dropzone.addEventListener(
        evt,
        (e) => {

          e.preventDefault();

          dropzone.classList.remove(
            "dragover"
          );

        }
      );

    }
  );


  dropzone.addEventListener(
    "drop",
    (e) => {

      const file =
        e.dataTransfer.files[0];

      if (file) {

        fileInput.files =
          e.dataTransfer.files;

        handleFileSelected(file);

      }

    }
  );


  fileInput.addEventListener(
    "change",
    () => {

      if (fileInput.files[0]) {

        handleFileSelected(
          fileInput.files[0]
        );

      }

    }
  );


  function handleFileSelected(file) {

    selectedFile = file;

    filenameLabel.textContent =
      file.name;

    runButton.disabled = false;

    setStatus("");

  }


  runButton.addEventListener(
    "click",
    async () => {

      if (!selectedFile) return;

      runButton.disabled = true;

      setStep("transcribe");

      setStatus(
        "文字起こし・情報抽出を実行中です…"
      );

      const formData =
        new FormData();

      formData.append(
        "file",
        selectedFile
      );


      try {

        const response =
          await fetch(
            "/api/process",
            {
              method: "POST",
              body: formData
            }
          );


        const data =
          await response.json();


        if (!response.ok) {

          throw new Error(
            data.error ||
            "処理中にエラーが発生しました"
          );

        }


        setStep("extract");

        setStatus(
          "情報抽出が完了しました。結果を表示しています…"
        );

        renderResult(data);


        setStep("review");

        setStatus(
          "完了しました。内容を確認してください。"
        );


      } catch (err) {

        setStep("upload");

        setStatus(
          err.message,
          true
        );


      } finally {

        runButton.disabled = false;

      }

    }
  );


  function renderTagList(
    container,
    items,
    options
  ) {

    container.innerHTML = "";


    if (!items.length) {

      const span =
        document.createElement("span");

      span.className = "source";

      span.textContent =
        options.emptyText;

      container.appendChild(span);

      return;

    }


    items.forEach((item) => {

      const el =
        document.createElement("div");

      el.className =
        "tag-item" +
        (options.warn ? " warn" : "");


      const label =
        document.createElement("span");

      label.textContent =
        options.label(item);

      el.appendChild(label);


      if (options.source) {

        const source =
          document.createElement("span");

        source.className =
          "source";

        source.textContent =
          "「" +
          options.source(item) +
          "」";

        el.appendChild(source);

      }


      container.appendChild(el);

    });

  }


  function renderResult(data) {

    lastResult = data;

    emptyState.style.display =
      "none";

    karteForm.style.display =
      "block";


    document.getElementById(
      "chiefComplaint"
    ).value =
      data.chief_complaint || "";


    renderTagList(
      document.getElementById(
        "symptomsList"
      ),
      data.symptoms,
      {
        label: (s) =>
          s.normalized,

        source: (s) =>
          s.mentioned_as,

        emptyText:
          "症状に関するキーワードは検出されませんでした",
      }
    );


    renderTagList(
      document.getElementById(
        "medicationsList"
      ),
      data.current_medications,
      {
        label: (m) =>
          m.category,

        source: (m) =>
          m.mentioned_as,

        emptyText:
          "服薬に関する言及は検出されませんでした",
      }
    );


    renderTagList(
      document.getElementById(
        "allergyList"
      ),
      data.allergy_mentions,
      {
        label: (a) =>
          a,

        warn: true,

        emptyText:
          "アレルギーに関する言及は検出されませんでした",
      }
    );


    const notesList =
      document.getElementById(
        "notesList"
      );

    notesList.innerHTML = "";


    data.other_notes.forEach(
      (note) => {

        const li =
          document.createElement("li");

        li.textContent =
          note;

        notesList.appendChild(li);

      }
    );


    document.getElementById(
      "rawTranscript"
    ).textContent =
      data.raw_transcript;

  }


  document.getElementById(
    "downloadJson"
  ).addEventListener(
    "click",
    () => {

      if (!lastResult) return;


      lastResult.chief_complaint =
        document.getElementById(
          "chiefComplaint"
        ).value;


      lastResult.reviewer_notes =
        document.getElementById(
          "freeNotes"
        ).value;


      const blob =
        new Blob(
          [
            JSON.stringify(
              lastResult,
              null,
              2
            )
          ],
          {
            type:
              "application/json"
          }
        );


      const url =
        URL.createObjectURL(blob);


      const a =
        document.createElement("a");


      a.href = url;

      a.download =
        "karte_draft.json";

      a.click();


      URL.revokeObjectURL(url);

    }
  );


  document.getElementById(
    "resetForm"
  ).addEventListener(
    "click",
    () => {

      selectedFile = null;

      lastResult = null;

      fileInput.value = "";

      filenameLabel.textContent =
        "";

      runButton.disabled = true;

      karteForm.style.display =
        "none";

      emptyState.style.display =
        "block";

      setStep("upload");

      setStatus("");

    }
  );

})();
