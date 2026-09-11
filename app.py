import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="7C 비행 슈팅 끝판왕", page_icon="✈️", layout="centered")

st.title("🌍 7C 무한 슈팅: 리마스터 에디션")
st.markdown("유치한 이모티콘은 가라! **실제 오락실 고해상도 그래픽**이 적용되었습니다. \n* ⚡**레이저:** 100% 모이면 자동 발사! \n* 💣**필살기:** 화면 빈 곳 더블 터치(따닥)!")
st.markdown("---")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  body { display: flex; flex-direction: column; align-items: center; background-color: #0d1117; color: white; margin: 0; padding: 10px; touch-action: none; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
  canvas { border-radius: 12px; box-shadow: 0 8px 30px rgba(0, 200, 255, 0.3); border: 2px solid #30363d; cursor: crosshair;}
  
  .status-bar { width: 350px; display: flex; justify-content: space-between; font-weight: bold; font-size: 16px; margin-bottom: 8px; text-shadow: 1px 1px 2px black;}
  .energy-container { width: 350px; height: 16px; background: #21262d; border-radius: 8px; margin-bottom: 12px; border: 1px solid #484f58; position: relative; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);}
  #energy-bar { height: 100%; width: 0%; background: linear-gradient(90deg, #00f2fe, #4facfe, #f093fb, #f5576c); transition: width 0.1s; }
  #energy-text { position: absolute; top: -1px; left: 38%; font-size: 13px; font-weight: bold; text-shadow: 1px 1px 2px black;}

  .info-bar { width: 350px; display: flex; justify-content: space-between; font-size: 14px; font-weight: bold; margin-bottom: 5px; color: #58a6ff;}

  #game-over-screen { position: absolute; top: 250px; text-align: center; display: none; width: 350px;}
  #game-over-text { color: #ff7b72; font-size: 36px; font-weight: 900; text-shadow: 0 0 20px #ff7b72; margin-bottom: 25px; letter-spacing: 2px;}
  #btn-restart { padding: 14px 28px; font-size: 20px; font-weight: bold; background: linear-gradient(180deg, #e34c26, #b1361e); color: white; border: none; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 15px rgba(227, 76, 38, 0.4); transition: transform 0.1s;}
  #btn-restart:active { transform: scale(0.95); }
</style>
</head>
<body>
  
  <div class="status-bar">
      <span id="score" style="color: #f2cc60;">🏆 점수: 0</span>
      <span id="weapon" style="color: #79c0ff;">⚡무기: Lv.1</span>
  </div>
  
  <div class="info-bar">
      <span id="stage-name">📍 지역: 우주 궤도</span>
      <span id="bomb-ui">💣 폭탄: 2개 (더블터치)</span>
  </div>

  <div class="energy-container">
      <div id="energy-bar"></div>
      <span id="energy-text">0% (자동발사)</span>
  </div>

  <canvas id="gameCanvas" width="350" height="500"></canvas>

  <div id="game-over-screen">
      <div id="game-over-text">MISSION FAILED</div>
      <button id="btn-restart" onclick="resetGame()">🚀 재도전</button>
  </div>

<script>
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");
  
  // 🎨 글로벌 게임 그래픽 직수입 (고해상도 이미지 로딩)
  const imgPlayer = new Image(); imgPlayer.src = "https://raw.githubusercontent.com/kenneynl/Space-Shooter-Redux/master/PNG/playerShip1_blue.png";
  const imgNormal = new Image(); imgNormal.src = "https://raw.githubusercontent.com/kenneynl/Space-Shooter-Redux/master/PNG/Enemies/enemyBlack2.png";
  const imgBoss = new Image(); imgBoss.src = "https://raw.githubusercontent.com/kenneynl/Space-Shooter-Redux/master/PNG/Enemies/enemyRed5.png";
  const imgMeteor = new Image(); imgMeteor.src = "https://raw.githubusercontent.com/kenneynl/Space-Shooter-Redux/master/PNG/Meteors/meteorBrown_big1.png";
  const imgItem = new Image(); imgItem.src = "https://raw.githubusercontent.com/kenneynl/Space-Shooter-Redux/master/PNG/Power-ups/powerupYellow_star.png";

  let score = 0; let level = 1; let energy = 0; let bombs = 2; let weaponLevel = 1; let gameOver = false; let frameCount = 0;
  let isLaserActive = false; let laserTimer = 0;

  const player = { x: 155, y: 400, width: 45, height: 35, invincible: 0 };
  let bullets = []; let enemyBullets = []; let enemies = []; let items = []; let particles = []; let shockwaves = [];
  let backgroundStars = [];

  const stages = [
      { min: 0,   name: "우주 궤도", c1: "#000015", c2: "#1a0b2e" },
      { min: 50,  name: "푸른 바다", c1: "#001f3f", c2: "#0074D9" },
      { min: 100, name: "붉은 사막", c1: "#4a1c00", c2: "#b05e00" },
      { min: 150, name: "맨하튼 야경", c1: "#0b1021", c2: "#1f2f5c" },
      { min: 200, name: "화산 지대", c1: "#2b0000", c2: "#8a0303" },
      { min: 300, name: "사이버펑크", c1: "#0a0a2a", c2: "#3a0088" }
  ];

  function initBackground() {
      backgroundStars = [];
      for(let i=0; i<60; i++) {
          backgroundStars.push({ x: Math.random()*canvas.width, y: Math.random()*canvas.height, size: Math.random()*2+0.5, speed: Math.random()*4+1 });
      }
  }
  initBackground();

  function drawBackground() {
      let stg = stages[level - 1];
      let grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
      grad.addColorStop(0, stg.c1); grad.addColorStop(1, stg.c2);
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
      for(let b of backgroundStars) {
          b.y += b.speed + (level * 1.5);
          if(b.y > canvas.height) { b.y = -10; b.x = Math.random()*canvas.width; }
          ctx.beginPath(); ctx.arc(b.x, b.y, b.size, 0, Math.PI*2); ctx.fill();
      }
  }

  function checkLevelUpdate() {
      let newLevel = 1;
      for (let i = stages.length - 1; i >= 0; i--) {
          if (score >= stages[i].min) { newLevel = i + 1; break; }
      }
      if (newLevel !== level) {
          level = newLevel;
          document.getElementById("stage-name").innerText = "📍 지역: " + stages[level - 1].name;
      }
  }

  function addEnergy(amount) {
      if(isLaserActive) return;
      energy += amount;
      if (energy >= 100) { energy = 100; useLaser(); }
      document.getElementById("energy-bar").style.width = energy + "%";
      document.getElementById("energy-text").innerText = Math.floor(energy) + "%";
  }

  function useBomb() {
      if (bombs > 0 && !gameOver) {
          bombs--;
          document.getElementById("bomb-ui").innerText = "💣 폭탄: " + bombs + "개";
          shockwaves.push({x: canvas.width/2, y: canvas.height/2, radius: 10, life: 30}); // 핵폭발 충격파
          
          for(let e of enemies) {
              createExplosion(e.x + 20, e.y + 20, "#FF4500", 25);
              score += e.hp;
          }
          enemies = []; enemyBullets = []; player.invincible = 60;
          ctx.fillStyle = "white"; ctx.fillRect(0,0,canvas.width,canvas.height);
          checkLevelUpdate(); updateUI();
      }
  }

  function useLaser() {
      if (!gameOver && !isLaserActive) {
          energy = 0;
          document.getElementById("energy-bar").style.width = "0%";
          document.getElementById("energy-text").innerText = "⚠ 초고압 레이저 방출 ⚠";
          isLaserActive = true; laserTimer = 100; player.invincible = 100;
      }
  }

  let lastTap = 0;
  canvas.addEventListener('touchstart', function(e) {
      let currentTime = new Date().getTime();
      if (currentTime - lastTap < 300 && currentTime - lastTap > 0) { useBomb(); e.preventDefault(); }
      else { movePlayer(e.touches[0].clientX, e.touches[0].clientY, canvas.getBoundingClientRect()); }
      lastTap = currentTime;
  }, { passive: false });

  canvas.addEventListener('dblclick', function(e) { useBomb(); e.preventDefault(); });

  function createExplosion(x, y, color, count=15) {
      for(let i=0; i<count; i++) {
          particles.push({
              x: x, y: y, vx: (Math.random()-0.5)*15, vy: (Math.random()-0.5)*15,
              size: Math.random()*4+2, color: color, life: 25
          });
      }
  }

  function drawParticles() {
      for (let i = particles.length - 1; i >= 0; i--) {
          let p = particles[i];
          ctx.fillStyle = p.color; ctx.globalAlpha = p.life / 25;
          ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI*2); ctx.fill();
          ctx.globalAlpha = 1.0;
          p.x += p.vx; p.y += p.vy; p.life--;
          if (p.life <= 0) particles.splice(i, 1);
      }
      
      // 필살기 충격파 그리기
      for(let i=shockwaves.length-1; i>=0; i--) {
          let sw = shockwaves[i];
          ctx.strokeStyle = `rgba(0, 255, 255, ${sw.life/30})`; ctx.lineWidth = 15;
          ctx.beginPath(); ctx.arc(sw.x, sw.y, sw.radius, 0, Math.PI*2); ctx.stroke();
          sw.radius += 25; sw.life--;
          if(sw.life <=0) shockwaves.splice(i,1);
      }
  }

  function drawPlayer() {
      if (player.invincible > 0) {
          player.invincible--;
          if (frameCount % 6 < 3) return; 
      }
      // 엔진 부스터 화염
      ctx.fillStyle = (frameCount % 4 < 2) ? "#00ffff" : "#0055ff";
      ctx.beginPath(); ctx.arc(player.x + player.width/2, player.y + player.height + 5, Math.random()*6+4, 0, Math.PI*2); ctx.fill();
      
      // 비행기 진짜 이미지 출력
      if(imgPlayer.complete) ctx.drawImage(imgPlayer, player.x, player.y, player.width, player.height);
  }

  function updateUI() {
      document.getElementById("score").innerText = "🏆 점수: " + score;
      document.getElementById("weapon").innerText = "⚡Lv." + weaponLevel;
  }

  function update() {
      frameCount++; checkLevelUpdate();

      if (isLaserActive) {
          laserTimer--;
          let laserWidth = 70;
          let laserX = player.x + player.width/2 - laserWidth/2;
          let gradient = ctx.createLinearGradient(laserX, 0, laserX + laserWidth, 0);
          gradient.addColorStop(0, "rgba(0, 255, 255, 0.2)");
          gradient.addColorStop(0.5, "rgba(255, 255, 255, 0.9)");
          gradient.addColorStop(1, "rgba(0, 255, 255, 0.2)");
          
          ctx.fillStyle = gradient; ctx.shadowBlur = 30; ctx.shadowColor = "cyan";
          ctx.fillRect(laserX, 0, laserWidth, player.y + 10);
          ctx.shadowBlur = 0;

          for (let i = enemies.length - 1; i >= 0; i--) {
              if (enemies[i].x + enemies[i].w > laserX && enemies[i].x < laserX + laserWidth) {
                  createExplosion(enemies[i].x + 20, enemies[i].y + 20, "#00FFFF");
                  score += enemies[i].hp; enemies.splice(i, 1); updateUI();
              }
          }
          if (laserTimer <= 0) { isLaserActive = false; document.getElementById("energy-text").innerText = "0% (자동발사)"; }
      }

      if (frameCount % 10 === 0 && !isLaserActive) { 
          if (weaponLevel === 1) { bullets.push({x: player.x + player.width/2, y: player.y, color: '#FFD700', dx: 0}); } 
          else if (weaponLevel === 2) {
              bullets.push({x: player.x + 8, y: player.y+10, color: '#00FFFF', dx: 0});
              bullets.push({x: player.x + player.width-8, y: player.y+10, color: '#00FFFF', dx: 0});
          } else {
              bullets.push({x: player.x + player.width/2, y: player.y-10, color: '#FF00FF', dx: 0});
              bullets.push({x: player.x + 5, y: player.y+15, color: '#FF00FF', dx: -2.5});
              bullets.push({x: player.x + player.width-5, y: player.y+15, color: '#FF00FF', dx: 2.5});
          }
      }

      for (let i = bullets.length - 1; i >= 0; i--) {
          bullets[i].y -= 18; bullets[i].x += bullets[i].dx;
          if (bullets[i].y < 0) bullets.splice(i, 1);
      }

      let spawnRate = Math.max(15, 45 - Math.floor(score / 5));
      if (frameCount % spawnRate === 0) {
          let r = Math.random();
          if (r < 0.2) enemies.push({ x: Math.random()*(canvas.width-40), y: -50, img: imgMeteor, hp: 1, speed: 7, w: 40, h: 40, type: 'meteor' });
          else if (r < 0.4) enemies.push({ x: Math.random()*(canvas.width-60), y: -60, img: imgBoss, hp: 6, speed: 2, w: 60, h: 60, type: 'boss' });
          else enemies.push({ x: Math.random()*(canvas.width-40), y: -40, img: imgNormal, hp: 2, speed: 3.5, w: 40, h: 40, type: 'normal' });
      }

      for (let i = enemies.length - 1; i >= 0; i--) {
          let e = enemies[i];
          e.y += e.speed + (score / 200);
          
          if (e.type === 'boss' && frameCount % 70 === 0 && e.y > 0) {
              enemyBullets.push({ x: e.x + e.w/2, y: e.y + e.h, speed: 6 });
          }

          if (player.invincible <= 0 && 
              player.x + 5 < e.x + e.w - 5 && player.x + player.width - 5 > e.x + 5 &&
              player.y + 5 < e.y + e.h - 5 && player.y + player.height - 5 > e.y + 5) {
              createExplosion(player.x + 20, player.y + 20, "#FF0000", 40);
              gameOver = true;
          }
          if (e.y > canvas.height) enemies.splice(i, 1);
      }

      ctx.fillStyle = "#ff4d4d";
      for (let i = enemyBullets.length - 1; i >= 0; i--) {
          let eb = enemyBullets[i];
          eb.y += eb.speed;
          ctx.shadowBlur = 10; ctx.shadowColor = "red";
          ctx.beginPath(); ctx.arc(eb.x, eb.y, 6, 0, Math.PI*2); ctx.fill(); ctx.shadowBlur = 0;
          
          if (player.invincible <= 0 &&
              eb.x > player.x && eb.x < player.x + player.width &&
              eb.y > player.y && eb.y < player.y + player.height) {
              createExplosion(player.x + 20, player.y + 20, "#FF0000", 40);
              gameOver = true;
          }
          if (eb.y > canvas.height) enemyBullets.splice(i, 1);
      }

      for (let i = items.length - 1; i >= 0; i--) {
          let it = items[i];
          it.y += 3.5;
          if (player.x < it.x + 25 && player.x + player.width > it.x && player.y < it.y + 25 && player.y + player.height > it.y) {
              items.splice(i, 1);
              if (weaponLevel < 3) weaponLevel++;
              updateUI(); continue;
          }
          if (it.y > canvas.height) items.splice(i, 1);
      }

      for (let i = enemies.length - 1; i >= 0; i--) {
          let hit = false;
          for (let j = bullets.length - 1; j >= 0; j--) {
              if (bullets[j].x > enemies[i].x && bullets[j].x < enemies[i].x + enemies[i].w &&
                  bullets[j].y > enemies[i].y && bullets[j].y < enemies[i].y + enemies[i].h) {
                  bullets.splice(j, 1); enemies[i].hp--; hit = true; break;
              }
          }
          if (hit) {
              if (enemies[i].hp <= 0) {
                  createExplosion(enemies[i].x + enemies[i].w/2, enemies[i].y + enemies[i].h/2, "#FFD700", 20);
                  if (Math.random() < 0.1) items.push({ x: enemies[i].x + 10, y: enemies[i].y }); 
                  
                  let gainedEnergy = (enemies[i].type === 'boss') ? 18 : 6;
                  addEnergy(gainedEnergy);
                  
                  score += 1; enemies.splice(i, 1); updateUI();
              } else {
                  createExplosion(enemies[i].x + enemies[i].w/2, enemies[i].y + enemies[i].h/2, "white", 4); 
              }
          }
      }
  }

  function gameLoop() {
      if (gameOver) { document.getElementById("game-over-screen").style.display = "block"; return; }
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      drawBackground();
      update();
      drawParticles();
      
      // 적, 아이템 그리기 (이미지)
      for (let e of enemies) { if(e.img.complete) ctx.drawImage(e.img, e.x, e.y, e.w, e.h); }
      for (let item of items) { if(imgItem.complete) ctx.drawImage(imgItem, item.x, item.y, 25, 25); }
      
      for (let b of bullets) {
          ctx.shadowBlur = 15; ctx.shadowColor = b.color;
          ctx.fillStyle = "white"; ctx.beginPath();
          ctx.ellipse(b.x, b.y, 3.5, 14, 0, 0, Math.PI*2); ctx.fill();
          ctx.shadowBlur = 0;
      }
      
      drawPlayer();
      requestAnimationFrame(gameLoop);
  }

  function movePlayer(clientX, clientY, rect) {
      player.x = clientX - rect.left - player.width / 2; player.y = clientY - rect.top - player.height / 2;
      if (player.x < -10) player.x = -10;
      if (player.x + player.width > canvas.width + 10) player.x = canvas.width - player.width + 10;
      if (player.y < 0) player.y = 0;
      if (player.y + player.height > canvas.height) player.y = canvas.height - player.height;
  }

  canvas.addEventListener("touchmove", function(e) {
      e.preventDefault(); movePlayer(e.touches[0].clientX, e.touches[0].clientY, canvas.getBoundingClientRect());
  }, { passive: false });

  canvas.addEventListener("mousemove", function(e) { movePlayer(e.clientX, e.clientY, canvas.getBoundingClientRect()); });

  function resetGame() {
      score = 0; level = 1; energy = 0; bombs = 2; weaponLevel = 1; gameOver = false; frameCount = 0; isLaserActive = false;
      bullets = []; enemyBullets = []; enemies = []; items = []; particles = []; shockwaves = [];
      player.x = 155; player.y = 400; player.invincible = 0;
      document.getElementById("bomb-ui").innerText = "💣 폭탄: 2개 (더블터치)";
      document.getElementById("stage-name").innerText = "📍 지역: 우주 궤도";
      document.getElementById("game-over-screen").style.display = "none";
      initBackground(); addEnergy(0); updateUI(); gameLoop();
  }

  resetGame();
</script>
</body>
</html>
"""

components.html(game_html, height=750)
