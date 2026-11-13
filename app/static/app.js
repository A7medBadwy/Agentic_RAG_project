const $ = (id) => document.getElementById(id);
async function refreshDocuments(){
  try{
    const res=await fetch('/api/documents'); const data=await res.json();
    $('doc-count').textContent=data.documents.length;
    $('documents-list').innerHTML=data.documents.length ? data.documents.map(d=>`<div class="doc-row"><span>📄 ${escapeHtml(d.document_name||'Untitled')}</span><small>${escapeHtml(d.file_type||'')}</small></div>`).join('') : '<div class="empty">No documents indexed yet.</div>';
  }catch(e){$('documents-list').textContent='Could not load documents.'}
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
$('refresh-btn').addEventListener('click',refreshDocuments);
$('file-input').addEventListener('change',()=>{
  const count=$('file-input').files.length;
  $('upload-status').textContent=count?`${count} file${count===1?'':'s'} selected.`:'';
});
const dropzone=document.querySelector('.dropzone');
dropzone.addEventListener('dragover',e=>e.preventDefault());
dropzone.addEventListener('drop',e=>{
  e.preventDefault();
  const files=e.dataTransfer.files;
  if(!files.length)return;
  $('file-input').files=files;
  $('file-input').dispatchEvent(new Event('change',{bubbles:true}));
});
$('upload-btn').addEventListener('click',async()=>{
  const files=$('file-input').files;if(!files.length){$('upload-status').textContent='Choose at least one file.';return}
  const form=new FormData();for(const f of files)form.append('files',f);
  $('upload-btn').disabled=true;$('upload-status').textContent='Uploading and creating embeddings…';
  try{const r=await fetch('/api/upload',{method:'POST',body:form});const d=await r.json();if(!r.ok)throw new Error(d.detail||'Upload failed');$('upload-status').textContent=d.uploaded.map(x=>`${x.filename}: ${x.chunks_indexed} chunks`).join(' · ');$('file-input').value='';await refreshDocuments();}
  catch(e){$('upload-status').textContent=e.message}
  finally{$('upload-btn').disabled=false}
});
$('chat-form').addEventListener('submit',async(e)=>{
  e.preventDefault();const q=$('question').value.trim();if(!q)return;
  addMessage(q,'user');$('question').value='';$('chat-status').textContent='Agents are retrieving and analyzing evidence…';
  const pending=addMessage('Working…','assistant');
  try{
    const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
    const d=await r.json();if(!r.ok)throw new Error(d.detail||'Request failed');
    pending.textContent=d.answer;
    if(d.citations?.length){const cite=document.createElement('div');cite.className='citation';cite.textContent='Sources: '+d.citations.map(c=>`${c.document_name}, p. ${c.page_number}`).join(' · ');pending.appendChild(cite)}
    $('chat-status').textContent=`Evidence chunks: ${d.evidence_count} · Feedback rounds: ${d.feedback_rounds}`;
  }catch(err){pending.textContent='Error: '+err.message;$('chat-status').textContent=''}
});
function addMessage(text,role){const el=document.createElement('div');el.className='message '+role;el.textContent=text;$('chat-log').appendChild(el);$('chat-log').scrollTop=$('chat-log').scrollHeight;return el}
refreshDocuments();
