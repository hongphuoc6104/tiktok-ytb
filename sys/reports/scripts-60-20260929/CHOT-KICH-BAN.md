# Xác nhận chốt bộ 60 kịch bản — bài 81–140

Người dùng đã chốt bộ 60 kịch bản trong cuộc trao đổi này bằng nguyên văn phản hồi:

> chốt kịch bản này commit và push lên github.

Phạm vi là bộ 60 bài vừa bàn giao, từ heart đến thirsty, content revision 1. Nội dung nằm trong commit `a5bbf89d6c48145affd694d8441cb7a06c9970bf`. Đã đối chiếu bản content trong gói với revision 1 thật của đủ 60 job: trùng khớp từng byte.

## Trạng thái ghi nhận

- Người dùng đã chốt nội dung bộ 60 bài nêu trên.
- Pipeline chưa ghi được quyết định approve. Kiểm tra job đầu tiên `vocab-heart-script-081` báo `Protected implementation changed` vì 9 file mới trong `.agents/`.
- Đây là bản ghi phản hồi thật trong tài liệu bàn giao, không phải decision.json hay quyết định duyệt được tạo ngoài workflow. Không sửa reviews, revisions, SQLite hoặc baseline.
- Không tạo âm thanh, hình ảnh hay video. Không mở bước media.

## Vướng mắc integrity đã đối chiếu

Lệnh `integrity-diff vocab-heart-script-081` xác nhận các file mới:

- `.agents/orchestrator_2/BRIEFING.md`
- `.agents/orchestrator_2/GATE_STATUS.md`
- `.agents/orchestrator_2/progress.md`
- `.agents/worker_m1/BRIEFING.md`
- `.agents/worker_m1/handoff.md`
- `.agents/worker_m1/progress.md`
- `.agents/worker_m2/BRIEFING.md`
- `.agents/worker_m2/DISPATCH.md`
- `.agents/worker_m2/progress.md`

Người dùng cần quyết định khôi phục hoặc tự adopt-code theo quy tắc dự án trước khi pipeline tiếp nhận approve. Sau khi xử lý, kiểm tra lại revision của từng job; chỉ ghi lời chốt này cho đúng nội dung đã đối chiếu dưới đây. Không tạo job thay thế hoặc coi lời chốt này là quyền duyệt một revision có nội dung khác.

## Danh mục nội dung đã chốt

| Bài | Từ | Job | Revision | SHA256 của content.json |
|---|---|---|---|---|
| 81 | heart | `vocab-heart-script-081` | 1 | `84dffb06e8fe9f402336ca11345d85b46e9af855e469809e9c49a5ee959c47f8` |
| 82 | health | `vocab-health-script-082` | 1 | `11ba143e59dfee8477cf53763000444b941a11b514a766024582722abed26b18` |
| 83 | healthy | `vocab-healthy-script-083` | 1 | `0678d24dd8be71f7e2ba44098a321c42efe929bdeceab60297ee2b61b432345c` |
| 84 | strong | `vocab-strong-script-084` | 1 | `024b0b4f654be5bc249c465e89778541517f3845d34776500f95ba1e597edbdf` |
| 85 | sick | `vocab-sick-script-085` | 1 | `fea0a2aa4dd4fcb8b2662522853e0619ec704991c8ea5a64843ab3b84a26a9e8` |
| 86 | cold | `vocab-cold-script-086` | 1 | `07519aa18c31bc05112d3ea2f77f501e1aab705129c8806e9d116f67676d0c24` |
| 87 | sleep | `vocab-sleep-script-087` | 1 | `4536dd12b1aadd9fed287d20e4d0b49f6f5e54b1e7236de6726e99d006f90167` |
| 88 | hospital | `vocab-hospital-script-088` | 1 | `6e17b8f90979bf5a7274948d9292291ecb430fa90dae36b95af68f1ef04880de` |
| 89 | doctor | `vocab-doctor-script-089` | 1 | `f1c8f1224155e2a30bd36f091830ba26d90ee27914fcceeaffd05d35384cff38` |
| 90 | nurse | `vocab-nurse-script-090` | 1 | `8bd50f48d7d403347c3113ce45987b3c872d311b06fd1adb6f66814515f0d87c` |
| 91 | medicine | `vocab-medicine-script-091` | 1 | `91e62982a24f99499033007e97a26bc885acc561c699d5e9b6a108a8192333aa` |
| 92 | free | `vocab-free-script-092` | 1 | `f6dcf93b52e6f37d694a21c58dc43c395d5a3d2543858177c9ef02a9f742f9cb` |
| 93 | drink | `vocab-drink-script-093` | 1 | `2e3d6cb799d868de6998f9513136156b81e82bb11e401b8d8dbc46de99336602` |
| 94 | water | `vocab-water-script-094` | 1 | `784a2f209ac4b00123b581fed07faf606d938dbdb6b7a276708ef284b26b3967` |
| 95 | rice | `vocab-rice-script-095` | 1 | `335a48d95faada8fea93c429f33200f65f28537c56f3ec3cc4b638a9dbe31772` |
| 96 | bread | `vocab-bread-script-096` | 1 | `a2f2272bf3c048dcb7bab8d851e5a212f355935eebf640eb98f50c62210836ca` |
| 97 | noodle | `vocab-noodle-script-097` | 1 | `824f1239f56614f662f3cc8a92ce1887f87d00e04f334c394f13b3a4e2ebdfb6` |
| 98 | soup | `vocab-soup-script-098` | 1 | `baba24f0bc47dca0e07d4479fd9cbc82f8f0e3a5fa7144cf81e3aa9e24ec8650` |
| 99 | egg | `vocab-egg-script-099` | 1 | `7dae3a2350052911a34a34e430113a43b0f628305083c501ee4ade290c4ae2f9` |
| 100 | meat | `vocab-meat-script-100` | 1 | `75a279ca2f4e7880c42db7d805a5cfb99844ef68ffaaf1f1914ebda286dc8988` |
| 101 | beef | `vocab-beef-script-101` | 1 | `559a815ed61df7aa3fa976b24067a303f3a366de61c71c2112ad6c24b720c438` |
| 102 | pork | `vocab-pork-script-102` | 1 | `c65c5ffb2ec7ae03774c5a5a4db79657cf6a6446f9591fa756eda4be94ad8070` |
| 103 | chicken | `vocab-chicken-script-103` | 1 | `c1b93eb4f36f506b28c76ec0459c02b454feaea257d4bf24dd359861c1e39e56` |
| 104 | fish | `vocab-fish-script-104` | 1 | `050931bfdb8315a8bc8ea4aaafa89e548e419bab21acf54c2f1d260061429769` |
| 105 | vegetable | `vocab-vegetable-script-105` | 1 | `53c151dc407c6c1683557dc217fe2cb746be6a87531a530ce65adf3856d61c73` |
| 106 | fruit | `vocab-fruit-script-106` | 1 | `30161008fc369ea37f8668a8b81cf83938b0f5d0b4ee08b984913ef98bbe5640` |
| 107 | apple | `vocab-apple-script-107` | 1 | `011e873daeb4b761a2905cb6f42f558f7b3537356d3a3ebfbed603bc8d9bacde` |
| 108 | banana | `vocab-banana-script-108` | 1 | `4ce5874f0cc24d05a9ac5d00e9cd2bf698fd43909e4046a91bb9f0f1fa8f4151` |
| 109 | orange | `vocab-orange-script-109` | 1 | `fe697e9de9faa4dafc6febdccf74f7dd21ecaaf429748eb2e5f29bbb689ecb08` |
| 110 | mango | `vocab-mango-script-110` | 1 | `ba56c5190af54692b8b4e634a29021c712023c8f7370cf84ea2642f6521df8cc` |
| 111 | tomato | `vocab-tomato-script-111` | 1 | `fdea4a2cef8e853d61266705feefd483e410b8a989f0c68b302b056d2eef5b29` |
| 112 | potato | `vocab-potato-script-112` | 1 | `e863d3a047ed736685c31cda61cb3ffa761132d5eec1194bc5d156949cfa38d6` |
| 113 | carrot | `vocab-carrot-script-113` | 1 | `c04eff580c8bf4459491b2ac6e4e370c1ae3eaec3b7b07d9ea6d674c07912577` |
| 114 | salad | `vocab-salad-script-114` | 1 | `79b67a8eede1e99d95072d8c7ecbd531ff647aec9e25a0cc62da6212fbe81374` |
| 115 | sandwich | `vocab-sandwich-script-115` | 1 | `dc66fa0e7c460e87c90931efb97f017b1135404f253a6e4d7828e279e2856c30` |
| 116 | pizza | `vocab-pizza-script-116` | 1 | `f62753bb5199e1728a3d357c026d0874c9963387e324947099f82b75675bb807` |
| 117 | cheese | `vocab-cheese-script-117` | 1 | `4efddc99ede8a10dbfb950ffe756c2d11931f7624d977d1150a45296743391ce` |
| 118 | butter | `vocab-butter-script-118` | 1 | `64b4a96de8897a3f38f7e19fe22dada22575967d476051ab148e5703eaf18e62` |
| 119 | milk | `vocab-milk-script-119` | 1 | `cddcad8d215ad09e19f3d4648efc746c8a69c3ff42b68a5bd5201e33f52afd8c` |
| 120 | sugar | `vocab-sugar-script-120` | 1 | `143a621b92aeb990e367cdf21c00cfc0840ea528e459fddc3c689bbc956f4c70` |
| 121 | salt | `vocab-salt-script-121` | 1 | `2372f970f2f75d28358d7c2825b96e8d7f9be73e6ac58c642c949c97547171a6` |
| 122 | cake | `vocab-cake-script-122` | 1 | `9fbc6c2bac2b5a90489cd6467e6a046c80d4e7d3943c8911d2ed12072064d255` |
| 123 | cookie | `vocab-cookie-script-123` | 1 | `60de63eea09084e68aa56fedd4bfd51225b4491dbefefce74495142bd076f9be` |
| 124 | chocolate | `vocab-chocolate-script-124` | 1 | `268135102594b9713e58c736dafcea8d6d1b093beed27086daa5bd3428670b21` |
| 125 | candy | `vocab-candy-script-125` | 1 | `dbd6c3734e4d9cfd4b0e9c40fde75aaf97c231d2647b9ccb4659a479ae7f91de` |
| 126 | ice cream | `vocab-ice-cream-script-126` | 1 | `1ee994c83a9ddc47adec0a472c31f00a6c512ee9cbf2f5c7e945536ed95903c7` |
| 127 | tea | `vocab-tea-script-127` | 1 | `a5554763845cfb32aca413e1cb1b2bd6ab4c42e725c9854c9123398bdbe5eb6d` |
| 128 | coffee | `vocab-coffee-script-128` | 1 | `ebd330b13c8ca05d5961353196de0f02ddc751656c13014715d573f7a79aebba` |
| 129 | juice | `vocab-juice-script-129` | 1 | `d7042e18cbbeb431506e94cdf9aeb0f4b812ada4d9706c358cad405ffa33b5e9` |
| 130 | beer | `vocab-beer-script-130` | 1 | `b597d227aab93dfc7bb12df6fefd28472a5651dc22067aa2e2e2372b000080e1` |
| 131 | menu | `vocab-menu-script-131` | 1 | `49094165f3e717530809d06481ace5097eadeaa11ddcfd19ff38813f7e8db8da` |
| 132 | order | `vocab-order-script-132` | 1 | `c4afd0f40ad971cb4ed7afd6537245cee0118f74063ff8a744c1bb872256e0b2` |
| 133 | waiter | `vocab-waiter-script-133` | 1 | `f1727fbf04a0917d94ca4025d44f6475d96151e8e28c129f130e0ff81e7333f1` |
| 134 | restaurant | `vocab-restaurant-script-134` | 1 | `4613bbfc85f583d95a312444304423e6fbd7f0732ffcd0934d465fd14b7661b5` |
| 135 | cafe | `vocab-cafe-script-135` | 1 | `d76828cff931639733b72cb22b826ec62937a27bc9d2e26678fbe7b56378988e` |
| 136 | sweet | `vocab-sweet-script-136` | 1 | `293664431785b1f569cc993e110a5a6fe35b6e4868ac6cebc7b1de077f631566` |
| 137 | fresh | `vocab-fresh-script-137` | 1 | `41c8528fbbf2e2af93f5924be9c56b882ed8dda68451f7c5d0d43fb801372e42` |
| 138 | delicious | `vocab-delicious-script-138` | 1 | `9058959f5db749c55ec3239d5f70f53fa2fec4f0ab980d6b7a770c5b6d9904f3` |
| 139 | hungry | `vocab-hungry-script-139` | 1 | `b08c7cb254d3af50f1f64a12bf124aaf3977d0dc0b495080bbfba8ae8468cfd7` |
| 140 | thirsty | `vocab-thirsty-script-140` | 1 | `4977706b7b8dba326271507b20832c43f67a25a84fb6c87def32c84e9a768033` |
