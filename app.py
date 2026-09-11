import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="7C 비행 슈팅", page_icon="✈️", layout="centered")

st.title("✈️ 7C 비행 슈팅: 에일리언 소탕 작전")
st.markdown("비행기를 잡고 움직이세요! **미사일은 자동 발사**됩니다. 적을 격추하고 **⭐(아이템)**을 먹어 무기를 진화시키세요!")
st.markdown("---")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  body { display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 0; touch-action: none; background-color: #f0f2f6; }
  canvas { background: #000022; border-radius: 10px; box-shadow: 0 6px 12px rgba(0,0,0,0.4); }
  #score-board { font-size: 20px; font-family: 'Arial', sans-serif; font-weight: bold; margin-bottom: 10px; display: flex; justify-content: space-between; width: 350px; color: #333; }
  #game-over { color: #FF4B4B; font-size: 24px; font-weight: bold; display: none; margin-top: 15px; text-align: center; }
  #btn-restart { margin-top: 15px; padding: 12px 24px; font-size: 18px; cursor: pointer; background: #FF4B4B; color: white; border: none; border-radius: 8px; display: none; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
</style>
</head>
<body>
  <div id="score-board">
      <span id="score">💥 격추: 0 기</span>
      <span id="weapon" style="color: #0055ff;">⚡ 무기: Lv.1</span>
  </div>
  <canvas id="gameCanvas" width="350" height="500"></canvas>
  <div id="game-over">🔥 비행기가 파괴되었습니다!</div>
  <button id="btn-restart" onclick="resetGame()">🔄 다시 출격하기</button>

<script>
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");
  let score = 0;
  let gameOver = false;
  let weaponLevel = 1;
  let frameCount = 0;
  let animationId;

  const player = { x: 155, y: 420, width: 40, height: 40, emoji: "✈️" };
  let bullets = [];
  let enemies = [];
  let items = [];

  function drawText(text, x, y, size) {
      ctx.font = size + "px Arial";
      ctx.fillText(text, x, y);
  }

  function drawBullets() {
      for (let b of bullets) {
          ctx.fillStyle = b.color;
          ctx.beginPath();
          ctx.arc(b.x, b.y, b.r, 0, Math.PI*2);
          ctx.fill();
      }
  }

  function update() {
      frameCount++;
      
      // 🚀 무기 레벨에 따른 자동 미사일 발사
      if (frameCount % 12 === 0) { // 발사 속도
          if (weaponLevel === 1) {
              // 1단계: 노란색 단발
              bullets.push({x: player.x + 20, y: player.y, r: 4, color: '#FFD700', dx: 0});
          } else if (weaponLevel === 2) {
              // 2단계: 하늘색 쌍발
              bullets.push({x: player.x + 5, y: player.y + 10, r: 4, color: '#00FFFF', dx: 0});
              bullets.push({x: player.x + 35, y: player.y + 10, r: 4, color: '#00FFFF', dx: 0});
          } else {
              // 3단계: 주황색 3방향 확산
              bullets.push({x: player.x + 20, y: player.y, r: 5, color: '#FF4500', dx: 0});
              bullets.push({x: player.x + 5, y: player.y + 10, r: 4, color: '#FF4500', dx: -1});
              bullets.push({x: player.x + 35, y: player.y + 10, r: 4, color: '#FF4500', dx: 1});
          }
      }

      // 미사일 이동 로직
      for (let i = bullets.length - 1; i >= 0; i--) {
          bullets[i].y -= 10;
          bullets[i].x += bullets[i].dx;
          if (bullets[i].y < 0) bullets.splice(i, 1);
      }

      // 👾 적군 출현 로직 (점수가 오를수록 많이 나옴)
      let spawnRate = Math.max(15, 50 - Math.floor(score / 5));
      if (frameCount % spawnRate === 0) {
          let emojis = ["🛸", "👾", "🚁", "☄️"];
          let em = emojis[Math.floor(Math.random() * emojis.length)];
          enemies.push({ x: Math.random() * (canvas.width - 40), y: -40, emoji: em, hp: 1 });
      }

      // 적군 이동 및 플레이어 충돌 검사
      for (let i = enemies.length - 1; i >= 0; i--) {
          enemies[i].y += 3 + (score / 100); // 서서히 빨라짐
          
          if (player.x < enemies[i].x + 30 && player.x + 30 > enemies[i].x &&
              player.y < enemies[i].y + 30 && player.y + 30 > enemies[i].y) {
              gameOver = true;
          }

          if (enemies[i].y > canvas.height) enemies.splice(i, 1);
      }

      // ⭐ 무기 업그레이드 아이템 이동 및 획득 로직
      for (let i = items.length - 1; i >= 0; i--) {
          items[i].y += 3;
          if (player.x < items[i].x + 25 && player.x + 35 > items[i].x &&
              player.y < items[i].y + 25 && player.y + 35 > items[i].y) {
              items.splice(i, 1);
              if (weaponLevel < 3) weaponLevel++; // 최대 레벨 3
              document.getElementById("weapon").innerText = "⚡ 무기: Lv." + weaponLevel;
              score += 5; // 아이템 먹어도 점수 플러스
              document.getElementById("score").innerText = "💥 격추: " + score + " 기";
              continue;
          }
          if (items[i].y > canvas.height) items.splice(i, 1);
      }

      // 💥 미사일이 적을 맞췄을 때 (가장 짜릿한 부분!)
      for (let i = enemies.length - 1; i >= 0; i--) {
          let hit = false;
          for (let j = bullets.length - 1; j >= 0; j--) {
              if (bullets[j].x > enemies[i].x && bullets[j].x < enemies[i].x + 35 &&
                  bullets[j].y > enemies[i].y && bullets[j].y < enemies[i].y + 35) {
                  bullets.splice(j, 1);
                  hit = true;
                  break;
              }
          }
          if (hit) {
              // 10% 확률로 무기 업그레이드 별(아이템)을 떨어뜨림!
              if (Math.random() < 0.1) {
                  items.push({ x: enemies[i].x, y: enemies[i].y });
              }
              enemies.splice(i, 1); // 적 폭파
              score += 1;
              document.getElementById("score").innerText = "💥 격추: " + score + " 기";
          }
      }
  }

  function gameLoop() {
      if (gameOver) {
          document.getElementById("game-over").style.display = "block";
          document.getElementById("btn-restart").style.display = "block";
          return;
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      update();
      
      // 그리기
      drawText(player.emoji, player.x, player.y + 35, 40);
      for (let e of enemies) drawText(e.emoji, e.x, e.y + 30, 35);
      for (let item of items) drawText("⭐", item.x, item.y + 25, 25);
      drawBullets();

      animationId = requestAnimationFrame(gameLoop);
  }

  // 모바일/PC 컨트롤
  function movePlayer(clientX, clientY, rect) {
      player.x = clientX - rect.left - player.width / 2;
      player.y = clientY - rect.top - player.height / 2;
      if (player.x < 0) player.x = 0;
      if (player.x + player.width > canvas.width) player.x = canvas.width - player.width;
      if (player.y < 0) player.y = 0;
      if (player.y + player.height > canvas.height) player.y = canvas.height - player.height;
  }

  canvas.addEventListener("touchmove", function(e) {
      e.preventDefault();
      movePlayer(e.touches[0].clientX, e.touches[0].clientY, canvas.getBoundingClientRect());
  }, { passive: false });

  canvas.addEventListener("mousemove", function(e) {
      movePlayer(e.clientX, e.clientY, canvas.getBoundingClientRect());
  });

  function resetGame() {
      score = 0;
      gameOver = false;
      weaponLevel = 1;
      frameCount = 0;
      bullets = [];
      enemies = [];
      items = [];
      player.x = 155;
      player.y = 420;
      document.getElementById("score").innerText = "💥 격추: 0 기";
      document.getElementById("weapon").innerText = "⚡ 무기: Lv.1";
      document.getElementById("game-over").style.display = "none";
      document.getElementById("btn-restart").style.display = "none";
      gameLoop();
  }

  resetGame(); // 게임 시작
</script>
</body>
</html>
"""

components.html(game_html, height=650)
