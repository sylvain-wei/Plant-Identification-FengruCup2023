from py2neo import *
import os 
import json


class Encyclopedia():
    def __init__(self) -> None:
        self.graph = Graph('bolt://localhost:7687', auth = ('neo4j', 'Wsh021006'))
        
        # 植物的性状
        self.charas = ["生活型", "高度", "叶片形状", "叶片颜色", "花朵形状", "花朵颜色", "果实形状", "果实颜色",
                       "树皮形状", "树皮颜色",
                       "温度", "光照", "保护和改造环境价值", "药用价值", "食用价值", "工业价值", "栽培价值", 
                       "抗逆性", "病害名称", "虫害名称"]
        # self.node_basic_attris = ['中文名', '别名', '描述']
        self.node_basic_attris = ['中文名', '别名']
        self.distri_attris = {'省份': 'Province', '地区': 'Area', '国家': 'Country'}
        self.family_attris = {'界': 'Kingdom', '门': 'Phylum', '纲': 'Class', '目': 'Order', '科': 'Family', '属': 'Genus'}
        self.attris_list = self.node_basic_attris + list(self.distri_attris.keys()) + list(self.family_attris.keys())
        self.attris_dict = {}
        self.attris_dict.update(self.distri_attris)
        self.attris_dict.update(self.family_attris)
        self.attri_chara_template_dict = self.attri_chara_template()
        self.other_option = "以上选项都不是您想要找的植物的信息。"
        # self.other_option_attri = "以上选项都不是您想要找的属性信息"

    def attri_chara_template(self):
        template_dict = {}
        for attri in self.node_basic_attris:
            template_dict[attri] = '它的{0}为'.format(attri)
        for chara in self.charas:
            if '颜色' in chara or '形状' in chara:
                template_dict[chara] = '它的{0}主要有'.format(chara)
            elif '高度' in chara:
                template_dict[chara] = '该种植物的{0}一般为'.format(chara)
            elif '温度' in chara or '光照' in chara:
                template_dict[chara] = '这种植物生长的{0}条件为'.format(chara)
            elif '价值' in chara:
                template_dict[chara] = '在{0}方面，其可以用于或用作'.format(chara)
            elif '害' in chara:
                template_dict[chara] = '其易得的{0}是'.format(chara)
            elif '抗逆性' in chara:
                template_dict[chara] = '这种植物的抗逆特性为'
            elif '生活型' in chara:
                template_dict[chara] = '它的生活型为'
        for attri in self.distri_attris:
            if attri == '省份':
                template_dict[attri] = '该植物广泛分布的省(市、区)有'.format(attri)
            elif attri in ('地区', '国家'):
                template_dict[attri] = '所属的{0}为'.format(attri)
        for attri in self.family_attris:
            template_dict[attri] = ''

        return template_dict

    #TODO:根据前端进行修改
    def output(self, string):
        """输出到终端。目前是标准输出，但之后可能是对接前端"""
        print(string, end='')

    def output_node_attributes(self, attris, node_attri_dict, template_dict, isFamilyOutput=False, returnString=False):
        if not returnString:
            for attri in attris:
                if attri not in node_attri_dict:
                    continue
                template = template_dict[attri]
                if type(node_attri_dict[attri]) == list and node_attri_dict[attri] != []:
                    self.output(template)

                    for idx, item in enumerate(node_attri_dict[attri]):
                        if idx != 0:
                            self.output('、')
                        self.output(item)
                    self.output('。')
                elif type(node_attri_dict[attri]) == str:
                    if not isFamilyOutput:
                        self.output(template)
                        self.output(node_attri_dict[attri].strip('。')+'。')
                    if isFamilyOutput:
                        if attri == '界':
                            self.output('该植物属于')
                        self.output(node_attri_dict[attri])
                        self.output(template)
                        if attri == '属':
                            self.output('。')
                        else:
                            self.output('，')
            self.output('\n')
        else:
            string = ''
            for attri in attris:
                if attri not in node_attri_dict:
                    continue
                template = template_dict[attri]
                if type(node_attri_dict[attri]) == list and node_attri_dict[attri] != []:
                    string += template

                    for idx, item in enumerate(node_attri_dict[attri]):
                        if idx != 0:
                            string += '、'
                        string += item
                    string += '。'
                elif type(node_attri_dict[attri]) == str:
                    if not isFamilyOutput:
                        string += template
                        string += node_attri_dict[attri].strip('。')+'。'
                    if isFamilyOutput:
                        if attri == '界':
                            string += '该植物属于'
                        string += node_attri_dict[attri]
                        string += template
                        if attri == '属':
                            string += '。'
                        else:
                            string += '，'
            # string += '\n'
            return string


    # def cypher(self, )

    def query(self, plant_sci_name):
        """根据植物的学名，在植物知识图谱中查找，打印输出植物的各方面数据"""
        # 植物的中文名、别名、全部性状（需要做成一个自然语言表达句来返回）
        # 植物学分类，x界x门xxx属...
        # 植物的分类
        # 植物的描述
        template_dict = self.attri_chara_template_dict

        n_matcher = NodeMatcher(self.graph)
        node = n_matcher.match("Species", name=plant_sci_name)

        # 1.根据学名，查找结点属性
        self.output('您要查询的植物为:'+plant_sci_name+'。\n')
        node_attri_dict = dict(node.all()[0]) # type(node.all()[0]) == Node
        # print(node_attri_dict, '\n^^^^^^^^^^^^')
        # TODO:考虑是否在每一个attri输出后加上换行符
        # 1.1.先输出基本信息
        self.output_node_attributes(self.node_basic_attris, node_attri_dict, template_dict)
            
        #1.2.其次，输出性状
        self.output_node_attributes(self.charas, node_attri_dict, template_dict)


        # 2.搜索所有的关系来输出结果

        # 2.1查询该物种分布的省份、地区、国家
        query_provinces = "MATCH (s:Species)-[:planted_in]->(p:{0}) WHERE s.name = '{1}' RETURN p.name".format('Province', plant_sci_name)
        query_areas = "MATCH (s:Species)-[:planted_in]->(p:{0}) WHERE s.name = '{1}' RETURN p.name".format('Area', plant_sci_name)
        query_country = "MATCH (s:Species)-[:planted_in]->(p:{0}) WHERE s.name = '{1}' RETURN p.name".format('Country', plant_sci_name)

        # 运行查询物种分布的省份、地区、国家
        results_provinces = self.graph.run(query_provinces)
        results_areas = self.graph.run(query_areas)
        results_country = self.graph.run(query_country)

        # 获得省份、地区、国家列表
        provinces = [record['p.name'] for record in results_provinces]
        areas = [record['p.name'] for record in results_areas]
        country = [record['p.name'] for record in results_country]
        
        distri_dict = {"省份": provinces, "地区": areas, "国家": country}
        self.output_node_attributes(self.distri_attris, distri_dict, template_dict)
        # 2.2查询该物种的界门纲目科属并输出字符串
        results_family = self.graph.run("MATCH (:Species {name: $name})-[:type_of]->(g:Genus)-[:subclass_of]->(f:Family)-[:subclass_of]->(o:Order)-[:subclass_of]->(c:Class)-[:subclass_of]->(p:Phylum)-[:subclass_of]->(k:Kingdom) RETURN g.name, f.name, o.name, c.name, p.name, k.name", name=plant_sci_name)
        results_family = results_family.data()[0]
        family_map = {'g.name': '属', 'f.name': '科', 'o.name': '目', 'c.name': '纲', 'p.name': '门', 'k.name': '界'}
        results_family = {family_map[key]: results_family[key] for key in family_map}
        # print(results_family)
        self.output_node_attributes(self.family_attris, results_family, template_dict, isFamilyOutput=True)


    def display_options(self, options:list[str], displayOtherOptions=True):
        """options:list[str]"""
        self.output("请选择以下选项中的一个:\n")
        final_options = options
        if displayOtherOptions:
            final_options.append(self.other_option)
        for i, option in enumerate(final_options):
            self.output("{0}.{1}".format(i+1, option)+'\n')

    def receive_text_message(self)->str:
        text = input()
        return text

    #TODO:根据前端进行修改
    def receive_option_message(self, options)->int:
        """
            options个数为候选植物的个数
            连接前端回收的内容，然后将前端中用户的选择结果返回
            由于只是一个选择框返回的序号，则option_id应该是一个数
        """
        # 第1步，先接收前端信息
        # 第2步，整合前端信息，返回option序号（从1开头）
        while(True):
            self.output("\n请您输入您选择的选项号：\n")
            option_id = input() #TODO:根据前端进行修改
            if not option_id.isdigit():
                self.output('您输入的内容有误，请您重新输入！\n')
            elif int(option_id) > len(options) or int(option_id) <= 0:
                self.output('您的选项号有误，请您重新选择！\n')
            else:
                break
        return int(option_id)

    def integrate_information(self, preliminary_results, hasGuidedUser=False):
        """
            1.接受鉴别系统给的初步鉴定结果
            2.查询若干结果的结点信息，并对比其性状，确定提问方式
            3.制作各种问题模板（独立成一个def函数）
            4.整合问题，并输出到终端，作为引导用户信息
            5.获取用户信息
            6.从用户反馈的回复
                若用户认为都不对，就不管了
                若用户选了至少一项，就选择这个结果
            7.将最终结果返回给百科系统
        """
        # 第一部分，这一部分是引导用户并获取用户的进一步确认信息
        if not hasGuidedUser:
            # 1. preliminary_results的形式：{植物学名i：置信度i}
            doFirst = len(preliminary_results) > 1
            # doSecond = False
            doSecond = True
            already_find = False
            final_plant = preliminary_results[0] if not doFirst else None
            if doFirst:
                # 2.查询结点信息，并对比其性状，确定提问方式
                # 2.1.查询结点信息
                plant_chara_dict = {}   # {plant1: {chara_name1:chara1value, chara_name2:chara2value}, plant2: {...}},是dict[dict]
                chara_plant_dict = {}   # {chara_name1: [plant1, plant2,...]},是dict[list]
                for plant_sci_name in preliminary_results:
                    n_matcher = NodeMatcher(self.graph)
                    node = n_matcher.match("Species", name=plant_sci_name)
                    node_attri_dict = dict(node.all()[0])
                    node_attri_dict.pop('描述')
                    node_attri_dict.pop('name')
                    plant_chara_dict[plant_sci_name] = node_attri_dict
                    for chara_name in node_attri_dict:
                        if chara_name not in chara_plant_dict:
                            chara_plant_dict[chara_name] = []
                        chara_plant_dict[chara_name].append(plant_sci_name)
                num_candidate_plants = len(plant_chara_dict)

                # 2.2.1.1第一种提问方式的数据准备
                common_charas = []  # 共有的性状名
                for chara_name in chara_plant_dict:
                    if len(chara_plant_dict[chara_name]) == num_candidate_plants:
                        # 如果所有候选植物都具有该种性状
                        # 暂时不过滤分不开的性状
                        # if chara_name != 
                        common_charas.append(chara_name)
                # test
                print('\n\n')
                # 2.2.1.2第一种提问方式的提示输出
                options1 = []
                id2plant = []   # 用于最后确定植物名
                for plant in plant_chara_dict:
                    option_content = ''
                    for chara_name in common_charas:
                            option_content = option_content + self.output_node_attributes([chara_name], plant_chara_dict[plant], self.attri_chara_template_dict, returnString=True)
                    # 组成字符串添加到options集合里
                    options1.append(option_content) 
                    id2plant.append(plant)
                # 2.2.1.3第一种提问方式的结果回收、分析
                self.display_options(options1)
                option_id = self.receive_option_message(options1)    # option_id:[1,...,n+1]
                # # 当option_id=n+1或answer_id=n时，就是没找到，在这种情况下才进行第二次提问
                doSecond = (option_id == len(options1))
                answer_id = option_id - 1   # 转换成[0, 1, ..., n]
                already_find = False if doSecond else True
                if already_find:
                    final_plant = id2plant[answer_id]

            if doSecond:
                # 2.2.2.1第二种方式的数据准备
                diff_plant_chara_dict = {}  # 这个dict的内容是：对于其中的plant，它下面的chara并非全部候选的plant都有的
                for plant in preliminary_results:
                    diff_plant_chara_dict[plant] = {}
                    for chara in plant_chara_dict[plant]:
                        if chara not in common_charas:
                            diff_plant_chara_dict[plant][chara] = plant_chara_dict[plant][chara]
                # 2.2.2.2第二种方式的提示输出
                options2 = []
                id2plant = []
                for plant in diff_plant_chara_dict:
                    option_content = ''
                    for chara_name in diff_plant_chara_dict[plant]:
                        option_content = option_content + self.output_node_attributes([chara_name], diff_plant_chara_dict[plant], self.attri_chara_template_dict, returnString=True)
                    if option_content != '':
                        id2plant.append(plant)
                        options2.append(option_content)
                if len(options2) == len(preliminary_results):
                    # 表示所有的植物都有至少一种不全有的性状
                    self.output('\n\n抱歉！由于第一次提示未能让您选择到合适的植物，以下是第二次提示：\n')
                    self.display_options(options2)
                    option_id = self.receive_option_message(options2)    # option_id:[1,...,n+1]
                    already_find = True if option_id != len(options2) else False
                    answer_id = option_id - 1   # 转换成[0, 1, ..., n]
                    if already_find:
                        final_plant = id2plant[answer_id]
                else:
                    self.output('对不起，您找到的植物不存在或系统无法根据您提供的信息确认植物类别！\n请您重试，谢谢！')
                    # return None     # 表示查找失败
            if final_plant:
                self.output('经过以上提示和您的进一步确认，得到以下信息：\n\n'.format(final_plant))
                self.query(final_plant)
                # return final_plant
            else:
                self.output('对不起，您找到的植物不存在或系统无法根据您提供的信息确认植物类别！\n请您重试，谢谢！')
                # return None     # 表示查找失败
            
            

    def query_by_basic_attris(self):
        """根据基本的属性例如植物学分类、省份、地区、国家来查找植物，返回植物名"""
        final_plant = None
        # 1.首先交互：用户输入要查询的属性名
        self.output('请选择您想要查询的属性：\n')
        self.display_options(self.attris_list, displayOtherOptions=False)
        option_id = self.receive_option_message(self.attris_list)
        answer_id = option_id - 1
        # 在这种情况下它选择的是查询别名
        query_plant_name = True if answer_id == 0  or answer_id == 1 else False
        if query_plant_name:
            # 如果是查找中文名/别名对应的植物
            self.output('请输入您想要查询的植物的{}：\n'.format(self.attris_list[answer_id]))
            text = self.receive_text_message()
            if self.attris_list[answer_id] == '中文名':
                # 如果是根据中文名查找植物
                query_c_name_node = 'MATCH (s:Species {中文名: "%s" }) RETURN s.name'%text
                result_c_name_node = self.graph.run(query_c_name_node)
                result_lst = [record["s.name"] for record in result_c_name_node]
                if result_lst == []:
                    self.output('没有找到您想要查询的植物！\n')
                else:
                    # 找到想要的植物了
                    final_plant = result_lst[0]
                    self.query(final_plant) # 返回该植物的全部信息
            else:
                # 如果是根据别名查找植物
                query_common_name_node = 'MATCH (s:Species)-[:has_common_name]->(c:CommonName { name: "%s" }) RETURN s.name' % text
                result_common_name_node = self.graph.run(query_common_name_node)
                result_lst = [record["s.name"] for record in result_common_name_node]
                if result_lst == []:
                    self.output('没有找到您想要查询的植物！\n')
                else:
                    # 找到想要的植物了
                    final_plant = result_lst[0]
                    self.query(final_plant) # 返回该植物的全部信息
                
                
        else:
            # 2.然后根据属性名，查询该属性类型的所有结点的名字
            attri_name = self.attris_list[answer_id]
            query_atrri_nodes = "MATCH (p:{0}) RETURN p.name".format(self.attris_dict[attri_name])
            result_attri_nodes = self.graph.run(query_atrri_nodes)
            candi_attri_node_names = [record["p.name"] for record in result_attri_nodes]
            # 3.再将这些候选属性结点的名字作为一个选项框全部发送给用户
            self.output("请您选择您想要具体查询的属性值：\n")
            self.display_options(candi_attri_node_names, displayOtherOptions=False)    # 将该属性下的所有候选属性值展示给用户
            option_id = self.receive_option_message(candi_attri_node_names)    # 接收用户的信息，得到选择的id
            answer_id = option_id - 1   # 将用户的选项序号转化为candi_attri_node_names列表下标
            attri_value = candi_attri_node_names[answer_id]  # 获得用户选择的属性值
            print(attri_value)
            # 4.细分属性类别进行查询
            # 4.1 第一种情况：植物学分类
            if attri_name in self.family_attris:
                # 首先根据属性名，查询该属性类型的所有结点的名字
                if attri_name == '属':
                    query_plant_nodes = 'MATCH (s:Species)-[:type_of]->(g:Genus { name:"%s" }) RETURN s.name, s.中文名' % attri_value
                else:
                    query_plant_nodes = 'MATCH (s: Species)-[:type_of]->(:Genus)-[:subclass_of*]->(f:%s { name:"%s" } ) RETURN s.name AS speciesName, s.中文名 AS speciesChName'%(self.attris_dict[attri_name], attri_value)
            elif attri_name in self.distri_attris:
                if attri_name == '省份':
                    query_plant_nodes = 'MATCH (s: Species)-[:planted_in]->(p:Province { name:"%s" }) RETURN s.name AS speciesName, s.中文名 AS speciesChName' % attri_value
                elif attri_name == '地区':
                    query_plant_nodes = 'MATCH (s: Species)-[:planted_in]->(:Province)-[:belongs_to]->(a:Area { name:"%s"}) RETURN DISTINCT s.name AS speciesName, s.中文名 AS speciesChName' % attri_value
                elif attri_name == '国家':
                    query_plant_nodes = 'MATCH (s: Species)-[:planted_in]->(:Province)-[:belongs_to]->(:Area)-[:belongs_to]->(:Country { name:"%s"}) RETURN DISTINCT s.name AS speciesName, s.中文名 AS speciesChName UNION MATCH (s: Species)-[:planted_in]->(:Country { name:"%s"}) RETURN s.name AS speciesName, s.中文名 AS speciesChName' % (attri_value, attri_value)

            
            result_plant_nodes = self.graph.run(query_plant_nodes)
            candi_plant_names = {record["speciesName"]: record['speciesChName'] for record in result_plant_nodes}
            candi_plant_ch2enNames = {candi_plant_names[plant]:plant for plant in candi_plant_names}
            if candi_plant_names == {}:
                if attri_name in self.family_attris:
                    self.output('没有植物拥有这种属性!\n')
                elif attri_name in self.distri_attris:
                    self.output('没有植物分布在这个地方！\n')
            elif len(candi_plant_names) == 1:
                # 只有一种植物的话
                final_plant = list(candi_plant_names.keys())[0]
            else:
                # 又让用户去从若干植物中去找
                self.display_options(list(candi_plant_ch2enNames.keys()), displayOtherOptions=False)  # debug
                option_id = self.receive_option_message(list(candi_plant_ch2enNames.keys()))
                answer_id = option_id - 1   # 将用户的选项序号转化为candi_attri_node_names列表下标
                final_plant = list(candi_plant_names.keys())[answer_id]  # 获得用户选择的最终植物
            if final_plant:
                self.query(final_plant)

            
            




pedia = Encyclopedia()
pedia.query('Chrysanthemum indicum')
pedia.integrate_information(['Diospyros kaki', "Diospyros lotus"])
pedia.query_by_basic_attris()